# 檔案：schemas.py
# 說明：定義 API 請求和回應的資料格式 (使用 Pydantic)。

from pydantic import BaseModel

class UserInDB(BaseModel):
    id: int
    email: str
    name: str | None = None
    picture: str | None = None
    role: str # 新增 role 欄位

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    
class AskRequest(BaseModel):
    question: str
