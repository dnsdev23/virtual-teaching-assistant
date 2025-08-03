# 檔案：crud.py
# 說明：包含所有對資料庫進行 CRUD (新增、讀取、更新、刪除) 的函式。
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
import models, schemas

# 載入環境變數
load_dotenv()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_or_update_user(db: Session, user_info: dict):
    """
    處理使用者登入。如果使用者是第一次登入，則建立新記錄。
    如果是第一次登入且 email 在 ADMIN_EMAILS 中，則設為 admin。
    """
    db_user = get_user_by_email(db, email=user_info["email"])
    
    admin_emails_str = os.environ.get("ADMIN_EMAILS", "")
    admin_emails = [email.strip() for email in admin_emails_str.split(',')]

    if db_user:
        # 對於已存在的使用者，只更新基本資料，不改變角色
        db_user.name = user_info.get("name")
        db_user.picture = user_info.get("picture")
    else:
        # 對於新使用者，檢查是否應設為 admin
        is_admin = user_info["email"] in admin_emails
        db_user = models.User(
            email=user_info.get("email"),
            name=user_info.get("name"),
            picture=user_info.get("picture"),
            role="admin" if is_admin else "user"
        )
        db.add(db_user)
        
    db.commit()
    db.refresh(db_user)
    return db_user
