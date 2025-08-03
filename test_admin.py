#!/usr/bin/env python3
"""
測試管理員功能的腳本
"""

import os
from dotenv import load_dotenv
from database import SessionLocal
import models, crud

# 載入環境變數
load_dotenv()

def test_admin_functionality():
    """測試管理員功能"""
    print("=== 測試管理員功能 ===")
    
    # 檢查 ADMIN_EMAILS 設定
    admin_emails_str = os.environ.get("ADMIN_EMAILS", "")
    admin_emails = [email.strip() for email in admin_emails_str.split(',')]
    print(f"設定的管理員郵箱: {admin_emails}")
    
    # 連接資料庫
    db = SessionLocal()
    
    try:
        # 查看現有使用者
        users = db.query(models.User).all()
        print(f"\n目前資料庫中的使用者數量: {len(users)}")
        
        for user in users:
            print(f"  - {user.email} (角色: {user.role})")
        
        # 模擬建立管理員使用者
        admin_email = "admin@test.com"
        if admin_email not in [user.email for user in users]:
            print(f"\n模擬建立管理員使用者: {admin_email}")
            # 暫時將此郵箱加入管理員列表
            os.environ["ADMIN_EMAILS"] = f"{admin_emails_str},{admin_email}" if admin_emails_str else admin_email
            
            admin_user_info = {
                "email": admin_email,
                "name": "測試管理員",
                "picture": "https://example.com/admin.jpg"
            }
            
            admin_user = crud.create_or_update_user(db, admin_user_info)
            print(f"建立的管理員: {admin_user.email} (角色: {admin_user.role})")
        
        # 模擬建立普通使用者
        user_email = "user@test.com"
        if user_email not in [user.email for user in users]:
            print(f"\n模擬建立普通使用者: {user_email}")
            
            user_info = {
                "email": user_email,
                "name": "測試使用者",
                "picture": "https://example.com/user.jpg"
            }
            
            normal_user = crud.create_or_update_user(db, user_info)
            print(f"建立的使用者: {normal_user.email} (角色: {normal_user.role})")
            
    finally:
        db.close()
    
    print("\n=== 測試完成 ===")

if __name__ == "__main__":
    test_admin_functionality()
