# 檔案：models.py
# 說明：定義資料庫中的資料表結構。

from sqlalchemy import Column, Integer, String
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String)
    picture = Column(String)
    role = Column(String, default="user", nullable=False) # 新增 role 欄位
