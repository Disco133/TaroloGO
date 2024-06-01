from datetime import datetime
from pydantic import BaseModel


class FeedbackCreate(BaseModel):
    user_id: int
    feedback_text: str
    feedback_datetime: datetime


class FeedbackOut(BaseModel):
    feedback_id: int
    user_id: int
    feedback_text: str
    feedback_datetime: datetime
    is_read: bool


class FeedbackRead(BaseModel):
    feedback_id: int
    feedback_text: str
    is_read: bool