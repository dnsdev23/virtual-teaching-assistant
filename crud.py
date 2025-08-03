# 檔案：crud.py
# 說明：包含所有對資料庫進行 CRUD (新增、讀取、更新、刪除) 的函式。
import os
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, case
import models, schemas
from typing import List, Dict

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
def create_quiz_attempt(db: Session, user_id: int, topic: str, quiz_data: dict) -> models.QuizAttempt:
    attempt = models.QuizAttempt(user_id=user_id, topic=topic, score=0.0)
    db.add(attempt)
    db.flush()
    for q_data in quiz_data['questions']:
        question = models.Question(quiz_attempt_id=attempt.id, question_text=q_data['question_text'], correct_answer_index=q_data['correct_answer_index'])
        db.add(question)
        db.flush()
        for c_text in q_data['choices']:
            db.add(models.Choice(question_id=question.id, choice_text=c_text))
    db.commit()
    db.refresh(attempt)
    return attempt

def get_quiz_attempt(db: Session, attempt_id: int):
    return db.query(models.QuizAttempt).options(joinedload(models.QuizAttempt.questions).joinedload(models.Question.choices)).filter(models.QuizAttempt.id == attempt_id).first()

def get_user_quiz_history(db: Session, user_id: int):
    return db.query(models.QuizAttempt).filter(models.QuizAttempt.user_id == user_id).order_by(models.QuizAttempt.created_at.desc()).all()

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
    return db.query(models.ExternalResource).filter(models.ExternalResource.tags.like(f"%{query}%")).all()

# --- Analytics & Recommendation CRUD ---
def log_rag_query(db: Session, user_id: int, question: str, answer: str):
    log_entry = models.RAGQueryLog(user_id=user_id, question=question, answer=answer)
    db.add(log_entry)
    db.commit()
    return log_entry

def get_all_query_logs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.RAGQueryLog).options(joinedload(models.RAGQueryLog.user)).order_by(models.RAGQueryLog.created_at.desc()).offset(skip).limit(limit).all()

def get_all_quiz_attempts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.QuizAttempt).options(joinedload(models.QuizAttempt.user)).order_by(models.QuizAttempt.created_at.desc()).offset(skip).limit(limit).all()

def get_user_weakest_topics(db: Session, user_id: int, limit: int = 3) -> List[Dict]:
    """找出使用者表現最差的主題"""
    results = db.query(
        models.QuizAttempt.topic,
        func.avg(models.QuizAttempt.score).label('average_score'),
        func.count(models.QuizAttempt.id).label('attempt_count')
    ).filter(models.QuizAttempt.user_id == user_id).group_by(models.QuizAttempt.topic).order_by('average_score').limit(limit).all()
    
    return [{"topic": r.topic, "average_score": r.average_score} for r in results if r.average_score < 70]

def get_most_queried_topics(db: Session, limit: int = 5) -> List[Dict]:
    """找出最常被提問的主題 (簡易版，計算提問次數)"""
    results = db.query(
        models.RAGQueryLog.question,
        func.count(models.RAGQueryLog.id).label('query_count')
    ).group_by(models.RAGQueryLog.question).order_by(func.count(models.RAGQueryLog.id).desc()).limit(limit).all()
    return [{"question": r.question, "count": r.query_count} for r in results]
