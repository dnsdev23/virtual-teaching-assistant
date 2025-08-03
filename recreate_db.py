#!/usr/bin/env python3
"""
重建資料庫腳本
用於重新建立包含新欄位的資料庫表格
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from database import Base, DATABASE_URL
import models

# 載入環境變數
load_dotenv()

def recreate_database():
    """重新建立資料庫表格"""
    print("正在重建資料庫...")
    
    # 建立引擎
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    
    # 刪除所有現有表格（如果存在）
    Base.metadata.drop_all(bind=engine)
    print("已刪除舊的資料表")
    
    # 建立所有表格
    Base.metadata.create_all(bind=engine)
    print("已建立新的資料表，包含 role 欄位")
    
    print("資料庫重建完成！")

if __name__ == "__main__":
    recreate_database()
