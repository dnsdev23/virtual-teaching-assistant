# 檔案：models.py
# 說明：定義資料庫中的資料表結構。

from sqlalchemy import Column, Integer, String, ForeignKey, Text, JSON, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String)
    picture = Column(String)
    role = Column(String, default="user", nullable=False)
    
    quiz_attempts = relationship("QuizAttempt", back_populates="user")
    query_logs = relationship("RAGQueryLog", back_populates="user")

class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    topic = Column(String) # 新增欄位來記錄測驗主題
    score = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="quiz_attempts")
    questions = relationship("Question", back_populates="quiz_attempt", cascade="all, delete-orphan")

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    quiz_attempt_id = Column(Integer, ForeignKey("quiz_attempts.id"))
    question_text = Column(Text, nullable=False)
    correct_answer_index = Column(Integer, nullable=False)
    user_answer_index = Column(Integer)
    is_correct = Column(String) # 'correct', 'incorrect', 'unanswered'
    
    quiz_attempt = relationship("QuizAttempt", back_populates="questions")
    choices = relationship("Choice", back_populates="question", cascade="all, delete-orphan")

class Choice(Base):
    __tablename__ = "choices"
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"))
    choice_text = Column(Text, nullable=False)
    
    question = relationship("Question", back_populates="choices")

class ExternalResource(Base):
    __tablename__ = "external_resources"
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False, unique=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    tags = Column(String) # Comma-separated tags for searching

class RAGQueryLog(Base):
    __tablename__ = "rag_query_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="query_logs")
