# 檔案：main.py
# 說明：FastAPI 主應用程式，整合所有功能。

import os
import json
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware
from typing import List

# 匯入我們自己的模組
import models, crud, auth, schemas
from database import engine, SessionLocal

# LangChain Agent 相關匯入
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.agents import tool, AgentExecutor, create_react_agent
from langchain_community.tools.google_search.tool import GoogleSearchRun
from langchain_community.utilities.google_search import GoogleSearchAPIWrapper

# Google 驗證相關匯入
from google_auth_oauthlib.flow import Flow

# 載入環境變數
load_dotenv()

# 在開發環境中允許不安全的傳輸 (僅限本地開發)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# 建立資料庫表格
models.Base.metadata.create_all(bind=engine)

# FastAPI App
app = FastAPI(title="虛擬助教 API (最終版)")

# 設定 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key=os.environ["SECRET_KEY"])

# --- 全域資源初始化 ---
try:
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3, convert_system_message_to_human=True)
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = Chroma(persist_directory="chroma_db", embedding_function=embeddings)
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    
    # 簡化的知識庫搜尋函數
    def search_knowledge_base(query: str) -> str:
        """搜尋課程知識庫"""
        try:
            docs = retriever.invoke(query)
            return "\n\n".join(doc.page_content for doc in docs)
        except Exception as e:
            return f"搜尋知識庫時發生錯誤: {e}"
    
    print("AI 系統初始化成功")
    ai_system_available = True

except Exception as e:
    print(f"無法初始化 AI 系統: {e}")
    ai_system_available = False
    search_knowledge_base = None

# --- Google 驗證設定 ---
flow = Flow.from_client_config(
    client_config={
        "web": {
            "client_id": os.environ['GOOGLE_CLIENT_ID'],
            "client_secret": os.environ['GOOGLE_CLIENT_SECRET'],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://127.0.0.1:8000/auth/callback"],
        }
    },
    scopes=['openid', 'https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile'],
    redirect_uri="http://127.0.0.1:8000/auth/callback"
)

# --- API 端點 ---

# 驗證 & 使用者
@app.get("/auth/login")
async def login_via_google(request: Request):
    authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')
    request.session['state'] = state
    return RedirectResponse(authorization_url)

@app.get("/auth/callback")
async def auth_callback(request: Request, db: Session = Depends(auth.get_db)):
    try:
        flow.fetch_token(authorization_response=str(request.url))
        
        # 正確地取得使用者資訊
        credentials = flow.credentials
        
        # 使用 Google API 取得使用者資訊
        import requests
        userinfo_response = requests.get(
            'https://www.googleapis.com/oauth2/v2/userinfo',
            headers={'Authorization': f'Bearer {credentials.token}'}
        )
        
        if not userinfo_response.ok:
            raise Exception("無法從 Google 取得使用者資訊")
            
        user_info = userinfo_response.json()
        
        user = crud.create_or_update_user(db, user_info)
        access_token = auth.create_access_token(data={"sub": user.email})
        
        # *** 修改這裡 ***
        # 從直接回傳 JSON 改為重新導向到前端的 callback 頁面
        frontend_callback_url = f"http://localhost:5173/auth/callback?token={access_token}"
        return RedirectResponse(frontend_callback_url)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"驗證失敗: {e}")

@app.get("/api/users/me", response_model=schemas.UserSchema)
async def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

# AI 問答 (簡化版本)
@app.post("/api/ask", response_model=dict)
async def ask_question(request: schemas.AskRequest, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(auth.get_db)):
    if not ai_system_available:
        raise HTTPException(status_code=503, detail="AI 系統尚未準備就緒。")
    
    try:
        # 搜尋知識庫
        context = search_knowledge_base(request.question)
        
        # 使用 LLM 產生回答
        prompt = f"""你是一個虛擬教學助理。請根據以下課程內容回答學生的問題。
        
課程內容：
{context}

學生問題：{request.question}

請提供準確、有幫助的回答："""
        
        response = llm.invoke(prompt)
        answer = response.content
        
        # 記錄查詢
        crud.log_rag_query(db, user_id=current_user.id, question=request.question, answer=answer)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"處理問題時發生錯誤: {e}")

# 測驗系統
@app.post("/api/quiz/generate", response_model=schemas.QuizAttemptSchema)
async def generate_quiz(req: schemas.GenerateQuizRequest, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(auth.get_db)):
    if not ai_system_available:
        raise HTTPException(status_code=503, detail="知識庫系統尚未準備就緒。")
        
    context_text = search_knowledge_base(req.topic)
    quiz_prompt = f"""請根據以下課程內容，為「{req.topic}」設計一份包含 {req.num_questions} 題單選題的測驗。嚴格依照 JSON 格式輸出。
    課程內容：---{context_text}---
    JSON 格式範例：{{"questions": [{{"question_text": "問題？", "choices": ["A", "B", "C"], "correct_answer_index": 0}}]}}"""
    try:
        response = llm.invoke(quiz_prompt)
        quiz_data = json.loads(response.content)
        attempt = crud.create_quiz_attempt(db, user_id=current_user.id, topic=req.topic, quiz_data=quiz_data)
        return attempt
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 產生測驗失敗或格式錯誤: {e}")

@app.post("/api/quiz/submit/{attempt_id}", response_model=schemas.QuizResultSchema)
async def submit_quiz(attempt_id: int, req: schemas.SubmitQuizRequest, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(auth.get_db)):
    attempt = crud.get_quiz_attempt(db, attempt_id)
    if not attempt or attempt.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="找不到指定的測驗或權限不足。")
    correct_count = 0
    for answer in req.answers:
        question = db.query(models.Question).filter(models.Question.id == answer.question_id, models.Question.quiz_attempt_id == attempt_id).first()
        if question:
            question.user_answer_index = answer.answer_index
            question.is_correct = "correct" if question.user_answer_index == question.correct_answer_index else "incorrect"
            if question.is_correct == "correct": correct_count += 1
    attempt.score = (correct_count / len(attempt.questions)) * 100 if attempt.questions else 0
    db.commit()
    db.refresh(attempt)
    return attempt

# 個人化 & 數據分析
@app.get("/api/quiz/history", response_model=List[schemas.QuizResultSchema])
async def get_my_quiz_history(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(auth.get_db)):
    return crud.get_user_quiz_history(db, user_id=current_user.id)

@app.get("/api/recommendations", response_model=List[schemas.LearningRecommendation])
async def get_learning_recommendations(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(auth.get_db)):
    weak_topics = crud.get_user_weakest_topics(db, user_id=current_user.id)
    recommendations = []
    for topic_data in weak_topics:
        recommendations.append(schemas.LearningRecommendation(
            recommendation_type="review_topic",
            topic=topic_data["topic"],
            reason=f"您在「{topic_data['topic']}」主題的平均測驗分數較低 ({topic_data['average_score']:.1f}分)，建議您多加複習。"
        ))
    return recommendations

# 管理員功能
@app.post("/api/admin/resources", response_model=schemas.ExternalResourceSchema, status_code=201)
async def add_resource(resource: schemas.ExternalResourceCreate, current_admin: models.User = Depends(auth.get_current_admin_user), db: Session = Depends(auth.get_db)):
    return crud.create_external_resource(db, resource)

@app.get("/api/admin/resources", response_model=List[schemas.ExternalResourceSchema])
async def list_resources(current_admin: models.User = Depends(auth.get_current_admin_user), db: Session = Depends(auth.get_db)):
    return crud.get_external_resources(db)

@app.delete("/api/admin/resources/{resource_id}", status_code=204)
async def remove_resource(resource_id: int, current_admin: models.User = Depends(auth.get_current_admin_user), db: Session = Depends(auth.get_db)):
    if not crud.delete_external_resource(db, resource_id):
        raise HTTPException(status_code=404, detail="找不到指定的資源。")
    return {"ok": True}

@app.get("/api/admin/analytics/query-logs", response_model=List[schemas.RAGQueryLogSchema])
async def get_query_logs(current_admin: models.User = Depends(auth.get_current_admin_user), db: Session = Depends(auth.get_db), skip: int = 0, limit: int = 100):
    return crud.get_all_query_logs(db, skip=skip, limit=limit)

@app.get("/api/admin/analytics/quiz-attempts", response_model=List[schemas.QuizAttemptAdminView])
async def get_quiz_attempts_analytics(current_admin: models.User = Depends(auth.get_current_admin_user), db: Session = Depends(auth.get_db), skip: int = 0, limit: int = 100):
    return crud.get_all_quiz_attempts(db, skip=skip, limit=limit)

@app.get("/api/admin/analytics/summary", response_model=schemas.AnalyticsSummary)
async def get_analytics_summary(current_admin: models.User = Depends(auth.get_current_admin_user), db: Session = Depends(auth.get_db)):
    if not llm:
        raise HTTPException(status_code=503, detail="AI 系統尚未準備就緒。")
    
    recent_queries = crud.get_all_query_logs(db, limit=20)
    quiz_attempts = crud.get_all_quiz_attempts(db, limit=20)
    
    queries_text = "\n".join([f"- {log.question}" for log in recent_queries])
    quiz_text = "\n".join([f"- 主題: {att.topic}, 分數: {att.score}" for att in quiz_attempts])

    summary_prompt = f"""
    你是一位數據分析專家和資深教師。請根據以下最近的學生互動數據，總結出 2-3 個最重要的教學洞察與建議。
    請用繁體中文、條列式、簡潔有力地提出具體建議。

    最近的學生提問：
    {queries_text}

    最近的測驗表現：
    {quiz_text}

    你的分析與建議：
    """
    try:
        response = llm.invoke(summary_prompt)
        return schemas.AnalyticsSummary(summary=response.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"產生分析摘要時發生錯誤: {e}")

@app.get("/")
def read_root():
    return {"message": "歡迎使用虛擬助教 API！請前往 /docs 查看 API 文件。"}

# 啟動服務器
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
