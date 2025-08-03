# 檔案：main.py
# 說明：FastAPI 主應用程式，整合所有功能。

import os
import json
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

# RAG 相關匯入
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# Google 驗證相關匯入
from google_auth_oauthlib.flow import Flow

# 載入環境變數
load_dotenv()

# 建立資料庫表格
models.Base.metadata.create_all(bind=engine)

# FastAPI App
app = FastAPI(title="虛擬助教 API")

# 設定 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key=os.environ["SECRET_KEY"])

# --- RAG 系統設定 ---
try:
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = Chroma(persist_directory="chroma_db", embedding_function=embeddings)
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", temperature=0.3, convert_system_message_to_human=True)
    retriever = vector_store.as_retriever(search_kwargs={"k": 5})
except Exception as e:
    print(f"無法初始化 RAG 系統: {e}")
    retriever = None
    llm = None

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

# 驗證相關
@app.get("/auth/login")
async def login_via_google(request: Request):
    authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')
    request.session['state'] = state
    return RedirectResponse(authorization_url)

@app.get("/auth/callback")
async def auth_callback(request: Request, db: Session = Depends(auth.get_db)):
    try:
        flow.fetch_token(authorization_response=str(request.url))
        user_info = flow.credentials.id_token
        user = crud.create_or_update_user(db, user_info)
        access_token = auth.create_access_token(data={"sub": user.email})
        return JSONResponse(content={"access_token": access_token, "token_type": "bearer"})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"驗證失敗: {e}")

# 使用者相關
@app.get("/api/users/me", response_model=schemas.UserInDB)
async def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user

# RAG 問答
@app.post("/api/ask", response_model=dict)
async def ask_question(request: schemas.AskRequest, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(auth.get_db)):
    if not retriever or not llm:
        raise HTTPException(status_code=503, detail="RAG 系統尚未準備就緒。")
    
    # 建立 RAG chain
    prompt = ChatPromptTemplate.from_template(
        "你是一位友善且專業的課程助教。請根據以下提供的課程內容和相關資源來回答問題。\n"
        "如果內容中找不到答案，請誠實地回答「根據我手邊的資料，我找不到相關的答案。」\n\n"
        "課程內容：\n{context}\n\n"
        "相關外部資源：\n{external_resources}\n\n"
        "學生的問題：\n{question}\n\n"
        "你的回答："
    )
    rag_chain = (
        {
            "context": retriever, 
            "question": RunnablePassthrough(),
            "external_resources": lambda q: "\n".join([f"- {res.title}: {res.url}" for res in crud.search_external_resources(db, q)])
        }
        | prompt
        | llm
        | StrOutputParser()
    )
    
    try:
        answer = rag_chain.invoke(request.question)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"處理問題時發生錯誤: {e}")

# 測驗系統
@app.post("/api/quiz/generate", response_model=schemas.QuizAttemptSchema)
async def generate_quiz(req: schemas.GenerateQuizRequest, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(auth.get_db)):
    if not retriever or not llm:
        raise HTTPException(status_code=503, detail="RAG 系統尚未準備就緒。")

    context_docs = retriever.invoke(req.topic)
    context_text = "\n".join([doc.page_content for doc in context_docs])

    quiz_prompt_template = f"""
    你是一位專業的出題老師。請根據以下提供的課程內容，設計一份關於「{req.topic}」的測驗，包含 {req.num_questions} 題單選題。
    請嚴格依照以下的 JSON 格式輸出，不要有任何多餘的文字或解釋。

    課程內容：
    ---
    {context_text}
    ---

    JSON 格式範例：
    {{
      "questions": [
        {{
          "question_text": "問題一的文字？",
          "choices": ["選項A", "選項B", "選項C", "選項D"],
          "correct_answer_index": 0
        }},
        {{
          "question_text": "問題二的文字？",
          "choices": ["選項A", "選項B", "選項C"],
          "correct_answer_index": 2
        }}
      ]
    }}
    """
    try:
        response = llm.invoke(quiz_prompt_template)
        quiz_data = json.loads(response.content)
        
        attempt = crud.create_quiz_attempt(db, user_id=current_user.id, quiz_data=quiz_data)
        return attempt
    except (json.JSONDecodeError, Exception) as e:
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
            if question.user_answer_index == question.correct_answer_index:
                question.is_correct = "correct"
                correct_count += 1
            else:
                question.is_correct = "incorrect"
    
    attempt.score = (correct_count / len(attempt.questions)) * 100 if attempt.questions else 0
    db.commit()
    db.refresh(attempt)
    return attempt

# 管理員功能
@app.post("/api/admin/resources", response_model=schemas.ExternalResourceSchema, status_code=201)
async def add_resource(resource: schemas.ExternalResourceCreate, current_admin: models.User = Depends(auth.get_current_admin_user), db: Session = Depends(auth.get_db)):
    return crud.create_external_resource(db, resource)

@app.get("/api/admin/resources", response_model=List[schemas.ExternalResourceSchema])
async def list_resources(current_admin: models.User = Depends(auth.get_current_admin_user), db: Session = Depends(auth.get_db)):
    return crud.get_external_resources(db)

@app.delete("/api/admin/resources/{resource_id}", status_code=204)
async def remove_resource(resource_id: int, current_admin: models.User = Depends(auth.get_current_admin_user), db: Session = Depends(auth.get_db)):
    success = crud.delete_external_resource(db, resource_id)
    if not success:
        raise HTTPException(status_code=404, detail="找不到指定的資源。")
    return {"ok": True}

@app.get("/")
def read_root():
    return {"message": "歡迎使用虛擬助教 API！請前往 /docs 查看 API 文件。"}

@app.get("/api/admin/status", response_model=dict)
async def get_admin_status(current_admin: models.User = Depends(auth.get_current_admin_user)):
    return {"message": f"歡迎管理員 {current_admin.name}! 您有權限訪問此頁面。"}
