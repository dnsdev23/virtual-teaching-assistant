# 檔案：schemas.py
# 說明：定義 API 請求和回應的資料格式 (使用 Pydantic)。

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# --- User Schemas ---
class UserSchema(BaseModel):
    id: int
    email: str
    name: Optional[str] = None
    role: str
    class Config: from_attributes = True

# --- Token Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str

# --- RAG Schemas ---
class AskRequest(BaseModel):
    question: str

# --- Quiz Schemas ---
class GenerateQuizRequest(BaseModel):
    topic: str
    num_questions: int = Field(default=3, gt=0, le=10)

class ChoiceSchema(BaseModel):
    id: int
    choice_text: str
    class Config: from_attributes = True

class QuestionSchema(BaseModel):
    id: int
    question_text: str
    choices: List[ChoiceSchema]
    class Config: from_attributes = True

class QuizAttemptSchema(BaseModel):
    id: int
    topic: str
    questions: List[QuestionSchema]
    class Config: from_attributes = True

class SubmitAnswer(BaseModel):
    question_id: int
    answer_index: int

class SubmitQuizRequest(BaseModel):
    answers: List[SubmitAnswer]

class QuestionResultSchema(QuestionSchema):
    correct_answer_index: int
    user_answer_index: Optional[int] = None
    is_correct: Optional[str] = None

class QuizResultSchema(BaseModel):
    id: int
    topic: str
    score: float
    created_at: datetime
    questions: List[QuestionResultSchema]
    class Config: from_attributes = True

# --- External Resource Schemas ---
class ExternalResourceCreate(BaseModel):
    url: str
    title: str
    description: Optional[str] = None
    tags: str

class ExternalResourceSchema(ExternalResourceCreate):
    id: int
    class Config: from_attributes = True

# --- Analytics Schemas ---
class RAGQueryLogSchema(BaseModel):
    id: int
    user: UserSchema
    question: str
    answer: str
    created_at: datetime
    class Config: from_attributes = True

class QuizAttemptAdminView(QuizResultSchema):
    user: UserSchema

class LearningRecommendation(BaseModel):
    recommendation_type: str # e.g., "review_topic", "practice_quiz"
    topic: str
    reason: str
    
class AnalyticsSummary(BaseModel):
    summary: str
