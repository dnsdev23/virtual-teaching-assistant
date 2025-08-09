# 檔案：auth.py
# 說明：處理所有驗證相關的邏輯，包括 JWT 的建立與驗證。

import os
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from dotenv import load_dotenv, dotenv_values
from pathlib import Path
import crud, models
from database import SessionLocal

# 載入環境變數（明確指定專案根目錄 .env 檔案）
ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=str(ENV_PATH), override=False, encoding="utf-8")
# 退回方案：若環境變數仍缺失，直接讀取 .env 並補入 os.environ
if not os.environ.get("SECRET_KEY"):
    for k, v in dotenv_values(str(ENV_PATH), encoding="utf-8").items():
        if k and v is not None and k not in os.environ:
            os.environ[k] = v
# 最終保險：仍沒有 SECRET_KEY 時，產生一次性金鑰避免崩潰（僅供本機啟動）
if not os.environ.get("SECRET_KEY"):
    os.environ["SECRET_KEY"] = os.urandom(32).hex()

SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = os.environ.get("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="無法驗證憑證",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user

async def get_current_admin_user(current_user: models.User = Depends(get_current_user)):
    """
    一個新的依賴項，用來驗證使用者是否為管理員。
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您沒有權限執行此操作"
        )
    return current_user
