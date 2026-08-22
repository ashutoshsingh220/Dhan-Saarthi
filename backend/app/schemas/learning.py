from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class QuizQuestionPublic(BaseModel):
    id: str
    question: str
    options: list[str]


class QuizSubmissionRequest(BaseModel):
    answers: list[int] = Field(..., min_length=1, max_length=10, description="Selected option index for each question")


class QuizResultResponse(BaseModel):
    score_percentage: float
    correct_count: int
    total_questions: int
    status: str  # COMPLETED or IN_PROGRESS
    feedback: str


class LearningModuleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    module_id: str
    title: str
    description: str
    category: str
    difficulty: str
    estimated_minutes: int
    lesson_content: dict
    status: str = "NOT_STARTED"
    completed_at: datetime | None = None
    quiz_score: float | None = None


class LearningProgressSummaryResponse(BaseModel):
    total_modules: int
    completed_modules: int
    in_progress_modules: int
    completion_percentage: float


class LearningRecommendationResponse(BaseModel):
    module_id: str
    title: str
    description: str
    reason: str
    estimated_minutes: int
