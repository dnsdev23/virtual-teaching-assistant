# 檔案：crud.py
# 說明：包含所有對資料庫進行 CRUD (新增、讀取、更新、刪除) 的函式。
import os
from sqlalchemy.orm import Session
import models, schemas
from typing import List

# --- User CRUD ---
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_or_update_user(db: Session, user_info: dict):
    db_user = get_user_by_email(db, email=user_info["email"])
    admin_emails = [email.strip() for email in os.environ.get("ADMIN_EMAILS", "").split(',')]
    if db_user:
        db_user.name = user_info.get("name")
        db_user.picture = user_info.get("picture")
    else:
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

# --- Quiz CRUD ---
def create_quiz_attempt(db: Session, user_id: int, quiz_data: dict) -> models.QuizAttempt:
    attempt = models.QuizAttempt(user_id=user_id, score=0.0)
    db.add(attempt)
    db.flush() # To get the attempt ID
    
    for q_data in quiz_data['questions']:
        question = models.Question(
            quiz_attempt_id=attempt.id,
            question_text=q_data['question_text'],
            correct_answer_index=q_data['correct_answer_index'],
            is_correct='unanswered'
        )
        db.add(question)
        db.flush() # To get the question ID
        for c_text in q_data['choices']:
            choice = models.Choice(question_id=question.id, choice_text=c_text)
            db.add(choice)
            
    db.commit()
    db.refresh(attempt)
    return attempt

def get_quiz_attempt(db: Session, attempt_id: int):
    return db.query(models.QuizAttempt).filter(models.QuizAttempt.id == attempt_id).first()

# --- External Resource CRUD ---
def create_external_resource(db: Session, resource: schemas.ExternalResourceCreate):
    db_resource = models.ExternalResource(**resource.model_dump())
    db.add(db_resource)
    db.commit()
    db.refresh(db_resource)
    return db_resource

def get_external_resources(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.ExternalResource).offset(skip).limit(limit).all()

def delete_external_resource(db: Session, resource_id: int):
    db_resource = db.query(models.ExternalResource).filter(models.ExternalResource.id == resource_id).first()
    if db_resource:
        db.delete(db_resource)
        db.commit()
        return True
    return False

def search_external_resources(db: Session, query: str) -> List[models.ExternalResource]:
    # A simple tag-based search
    return db.query(models.ExternalResource).filter(models.ExternalResource.tags.like(f"%{query}%")).all()
