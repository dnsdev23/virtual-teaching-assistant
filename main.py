# 檔案：main.py
# 說明：FastAPI 主應用程式，整合所有功能。

import os
import json
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, Request, Query
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
from langchain import hub

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
    # 全域 LLM 和嵌入模型
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3, convert_system_message_to_human=True)
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    print("AI 系統初始化成功")
    ai_system_available = True

except Exception as e:
    print(f"無法初始化 AI 系統: {e}")
    ai_system_available = False

# --- Helper 函式來動態載入 Retriever ---
def get_retriever_for_chapter(chapter: str, db: Session = None):
    """根據章節名稱動態載入對應的 ChromaDB retriever。"""
    # 優先從資料庫查找章節資訊
    if db:
        db_chapter = crud.get_chapter_by_name(db, chapter)
        if db_chapter and db_chapter.is_active:
            db_path = os.path.join("chroma_db", db_chapter.name)
            if os.path.exists(db_path):
                vector_store = Chroma(persist_directory=db_path, embedding_function=embeddings)
                return vector_store.as_retriever(search_kwargs={"k": 3})
    
    # 回退到直接文件系統查找
    db_path = os.path.join("chroma_db", chapter)
    if not os.path.exists(db_path):
        raise HTTPException(status_code=404, detail=f"找不到章節 '{chapter}' 的知識庫。")
    
    vector_store = Chroma(persist_directory=db_path, embedding_function=embeddings)
    return vector_store.as_retriever(search_kwargs={"k": 3})

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

# 新增：獲取章節列表
@app.get("/api/chapters", response_model=List[str])
async def get_chapters():
    """掃描資料庫資料夾並回傳所有可用的章節列表。"""
    db_root = "chroma_db"
    if not os.path.exists(db_root):
        return []
    chapters = [d for d in os.listdir(db_root) if os.path.isdir(os.path.join(db_root, d))]
    return sorted(chapters)

# 新增：從資料庫獲取章節列表
@app.get("/api/chapters/managed", response_model=List[schemas.ChapterListItem])
async def get_managed_chapters(db: Session = Depends(auth.get_db)):
    """從資料庫獲取已管理的章節列表"""
    chapters = crud.get_all_chapters(db, include_inactive=False)
    return chapters

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

# AI 問答 (更新：支援章節化)
@app.post("/api/ask", response_model=dict)
async def ask_question(
    request: schemas.AskRequest, 
    chapter: str = Query(..., description="選擇的章節"), # 新增 chapter 查詢參數
    current_user: models.User = Depends(auth.get_current_user), 
    db: Session = Depends(auth.get_db)
):
    if not ai_system_available:
        raise HTTPException(status_code=503, detail="AI 系統尚未準備就緒。")
    
    try:
        # 動態建立 Agent 工具
        retriever = get_retriever_for_chapter(chapter, db)
        
        @tool
        def course_knowledge_base_search(query: str) -> str:
            f"""當問題與 '{chapter}' 章節的課程內容、講義、作業或評分標準相關時，使用此工具來搜尋內部知識庫。"""
            docs = retriever.invoke(query)
            return "\n\n".join(doc.page_content for doc in docs)

        # 設定網路搜尋工具
        search = GoogleSearchAPIWrapper(
            google_api_key=os.environ.get("GOOGLE_API_KEY_SEARCH"), 
            google_cse_id=os.environ.get("GOOGLE_CSE_ID")
        )
        web_search_tool = GoogleSearchRun(api_wrapper=search)
        web_search_tool.name = "internet_search"
        web_search_tool.description = "當問題涉及即時資訊、最新版本、外部事件或在課程知識庫中找不到答案時，使用此工具進行網路搜尋。"
        
        tools = [course_knowledge_base_search, web_search_tool]
        agent_prompt = hub.pull("hwchase17/react")
        agent = create_react_agent(llm, tools, agent_prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

        response = agent_executor.invoke({"input": request.question})
        answer = response.get("output", "抱歉，我無法處理這個問題。")
        
        # 記錄查詢（包含章節資訊）
        crud.log_rag_query(db, user_id=current_user.id, question=f"[{chapter}] {request.question}", answer=answer)
        return {"answer": answer}
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"處理問題時發生錯誤: {e}")

# 測驗系統 (更新：支援章節化)
@app.post("/api/quiz/generate", response_model=schemas.QuizAttemptSchema)
async def generate_quiz(
    req: schemas.GenerateQuizRequest, 
    chapter: str = Query(..., description="選擇的章節"), # 新增 chapter 查詢參數
    current_user: models.User = Depends(auth.get_current_user), 
    db: Session = Depends(auth.get_db)
):
    if not ai_system_available:
        raise HTTPException(status_code=503, detail="AI 系統尚未準備就緒。")
    
    try:
        retriever = get_retriever_for_chapter(chapter, db)
        context_docs = retriever.invoke(req.topic)
        context_text = "\n".join([doc.page_content for doc in context_docs])
        
        # 建立題目生成提示
        quiz_prompt = f"""請根據以下關於 '{chapter}' 章節的課程內容，為「{req.topic}」設計一份包含 {req.num_questions} 題單選題的測驗。嚴格依照 JSON 格式輸出。
        
課程內容：
---
{context_text}
---

JSON 格式範例：
{{"questions": [{{"question_text": "問題？", "choices": ["A", "B", "C"], "correct_answer_index": 0}}]}}

請確保：
1. 問題與提供的課程內容相關
2. 選項具有挑戰性且合理
3. 正確答案索引從 0 開始計算
4. 嚴格遵循上述 JSON 格式
"""
        
        response = llm.invoke(quiz_prompt)
        quiz_data = json.loads(response.content)
        
        # 建立測驗記錄（包含章節資訊）
        attempt = crud.create_quiz_attempt(db, user_id=current_user.id, topic=f"{chapter} - {req.topic}", quiz_data=quiz_data)
        return attempt
        
    except HTTPException as e:
        raise e
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
# 章節管理
@app.post("/api/admin/chapters", response_model=schemas.ChapterSchema, status_code=201)
async def create_chapter(
    chapter: schemas.ChapterCreate, 
    current_admin: models.User = Depends(auth.get_current_admin_user), 
    db: Session = Depends(auth.get_db)
):
    """創建新章節"""
    # 檢查章節名稱是否已存在
    existing_chapter = crud.get_chapter_by_name(db, chapter.name)
    if existing_chapter:
        raise HTTPException(status_code=400, detail=f"章節名稱 '{chapter.name}' 已存在")
    
    # 檢查資料夾路徑是否存在
    if not os.path.exists(chapter.folder_path):
        # 自動創建資料夾結構
        os.makedirs(os.path.join(chapter.folder_path, "materials"), exist_ok=True)
        os.makedirs(os.path.join(chapter.folder_path, "question_bank"), exist_ok=True)
    
    return crud.create_chapter(db, chapter)

@app.get("/api/admin/chapters", response_model=List[schemas.ChapterSchema])
async def list_all_chapters(
    include_inactive: bool = False,
    current_admin: models.User = Depends(auth.get_current_admin_user), 
    db: Session = Depends(auth.get_db)
):
    """獲取所有章節（管理員）"""
    return crud.get_all_chapters(db, include_inactive=include_inactive)

@app.get("/api/admin/chapters/{chapter_id}", response_model=schemas.ChapterSchema)
async def get_chapter_detail(
    chapter_id: int,
    current_admin: models.User = Depends(auth.get_current_admin_user), 
    db: Session = Depends(auth.get_db)
):
    """獲取章節詳細資訊"""
    chapter = crud.get_chapter_by_id(db, chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="找不到指定的章節")
    return chapter

@app.put("/api/admin/chapters/{chapter_id}", response_model=schemas.ChapterSchema)
async def update_chapter(
    chapter_id: int,
    chapter_update: schemas.ChapterUpdate,
    current_admin: models.User = Depends(auth.get_current_admin_user), 
    db: Session = Depends(auth.get_db)
):
    """更新章節資訊"""
    updated_chapter = crud.update_chapter(db, chapter_id, chapter_update)
    if not updated_chapter:
        raise HTTPException(status_code=404, detail="找不到指定的章節")
    return updated_chapter

@app.patch("/api/admin/chapters/{chapter_id}/toggle", response_model=schemas.ChapterSchema)
async def toggle_chapter_status(
    chapter_id: int,
    current_admin: models.User = Depends(auth.get_current_admin_user), 
    db: Session = Depends(auth.get_db)
):
    """切換章節啟用/停用狀態"""
    chapter = crud.toggle_chapter_status(db, chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="找不到指定的章節")
    return chapter

@app.delete("/api/admin/chapters/{chapter_id}", status_code=204)
async def delete_chapter(
    chapter_id: int,
    current_admin: models.User = Depends(auth.get_current_admin_user), 
    db: Session = Depends(auth.get_db)
):
    """刪除章節"""
    if not crud.delete_chapter(db, chapter_id):
        raise HTTPException(status_code=404, detail="找不到指定的章節")
    return {"ok": True}

@app.post("/api/admin/chapters/{chapter_id}/reindex", status_code=200)
async def reindex_chapter(
    chapter_id: int,
    current_admin: models.User = Depends(auth.get_current_admin_user), 
    db: Session = Depends(auth.get_db)
):
    """重新索引指定章節的文檔"""
    chapter = crud.get_chapter_by_id(db, chapter_id)
    if not chapter:
        raise HTTPException(status_code=404, detail="找不到指定的章節")
    
    # 這裡可以調用索引函數重新建立該章節的向量資料庫
    try:
        # 檢查資料夾是否存在
        if not os.path.exists(chapter.folder_path):
            raise HTTPException(status_code=400, detail=f"章節資料夾不存在: {chapter.folder_path}")
        
        # 這裡可以實作重新索引的邏輯
        return {"message": f"章節 '{chapter.display_name}' 重新索引請求已提交"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重新索引失敗: {e}")

@app.get("/api/admin/folders", response_model=List[str])
async def get_available_folders(
    current_admin: models.User = Depends(auth.get_current_admin_user)
):
    """獲取可用的資料夾路徑列表"""
    folders = []
    
    # 掃描常見的資料夾結構
    base_paths = ['materials', 'data', 'content']
    
    for base_path in base_paths:
        if os.path.exists(base_path):
            try:
                for item in os.listdir(base_path):
                    item_path = os.path.join(base_path, item)
                    if os.path.isdir(item_path):
                        # 標準化路徑分隔符
                        folder_path = item_path.replace('\\', '/')
                        folders.append(folder_path)
            except (OSError, PermissionError):
                continue
    
    # 移除重複並排序
    folders = sorted(list(set(folders)))
    return folders

# 資源管理
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
