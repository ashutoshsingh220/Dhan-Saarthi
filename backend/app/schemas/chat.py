from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ChatMessageRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    session_id: str | None = Field(default=None, max_length=36)


class ChatMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    session_id: str
    message_id: int
    response: str
    created_at: datetime


class ChatSessionSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    session_id: str
    title: str
    updated_at: datetime


class ChatMessageDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    role: str
    content: str
    created_at: datetime
