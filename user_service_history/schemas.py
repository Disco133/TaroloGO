from datetime import datetime

from pydantic import BaseModel, Field


class UserServiceHistoryCreate(BaseModel):
    user_id: int
    service_id: int
    status_id: int


class UserServiceHistoryOut(BaseModel):
    history_id: int
    tarot_id: int
    user_id: int
    service_id: int
    status_id: int
    first_name: str
    second_name: str
    service_name: str
    service_price: float


class UserServiceHistoryUpdateReview(BaseModel):
    history_id: int
    review_title: str
    review_text: str
    review_value: int = Field(..., le=5, ge=1)
    review_date_time: datetime
