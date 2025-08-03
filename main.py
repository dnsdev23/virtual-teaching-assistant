# 檔案：main.py
# 說明：FastAPI 主應用程式，整合所有功能。

import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

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

# 設定 CORS (跨來源資源共用)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生產環境中應指定前端的網域
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 設定 SessionMiddleware 來處理 OAuth state
app.add_middleware(SessionMiddleware, secret_key=os.environ["SECRET_KEY"])

# --- RAG 系統設定 ---
try:
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = Chroma(persist_directory="chroma_db", embedding_function=embeddings)
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", temperature=0.3, convert_system_message_to_human=True)
    retriever = vector_store.as_retriever(search_kwargs={"k": 5})

    template = """
    你是一位友善且專業的課程助教。請根據以下提供的課程內容來回答問題。
    如果內容中找不到答案，請誠實地回答「根據我手邊的資料，我找不到相關的答案。」絕對不要自己編造答案。
    盡量引用答案是來自於哪一份資料。

    課程內容：
    {context}

    學生的問題：
    {question}

    你的回答：
    """
    prompt = ChatPromptTemplate.from_template(template)

    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
except Exception as e:
    print(f"無法初始化 RAG 系統: {e}")
    rag_chain = None

# --- Google 驗證設定 ---
flow = Flow.from_client_config(
    client_config={
        "web": {
            "client_id": os.environ['GOOGLE_CLIENT_ID'],
            "client_secret": os.environ['GOOGLE_CLIENT_SECRET'],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "redirect_uris": ["http://127.0.0.1:8000/auth/callback"],
        }
    },
    scopes=['openid', 'https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile'],
    redirect_uri="http://127.0.0.1:8000/auth/callback"
)

# --- API 端點 ---

@app.get("/auth/login")
async def login_via_google(request: Request):
    """重新導向到 Google 登入頁面。"""
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    request.session['state'] = state
    return RedirectResponse(authorization_url)

@app.get("/auth/callback")
async def auth_callback(request: Request, db: Session = Depends(auth.get_db)):
    """處理 Google 登入後的回調，並回傳 JWT。"""
    try:
        flow.fetch_token(authorization_response=str(request.url))
        credentials = flow.credentials
        user_info = credentials.id_token
        
        user = crud.create_or_update_user(db, user_info)
        access_token = auth.create_access_token(data={"sub": user.email})
        
        # 在真實應用中，你會重新導向到前端頁面並附上 token
        # 這裡為了方便測試，直接回傳 JSON
        return JSONResponse(content={"access_token": access_token, "token_type": "bearer"})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"驗證失敗: {e}")


@app.post("/api/ask", response_model=dict)
async def ask_question(request: schemas.AskRequest, current_user: models.User = Depends(auth.get_current_user)):
    """
    對 RAG 系統提問。使用者必須通過驗證。
    """
    if not rag_chain:
        raise HTTPException(status_code=503, detail="RAG 系統尚未準備就緒。")
    try:
        answer = rag_chain.invoke(request.question)
        # 未來可以在這裡記錄使用者的提問歷史
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"處理問題時發生錯誤: {e}")

@app.get("/api/users/me", response_model=schemas.UserInDB)
async def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    """取得目前登入使用者的個人資料。"""
    return current_user

@app.get("/api/admin/status", response_model=dict)
async def get_admin_status(current_admin: models.User = Depends(auth.get_current_admin_user)):
    """
    一個只有管理員能訪問的範例端點。
    """
    return {"message": f"歡迎管理員 {current_admin.name}! 您有權限訪問此頁面。"}

@app.get("/")
def read_root():
    return {"message": "歡迎使用虛擬助教 API！請前往 /docs 查看 API 文件。"}
