from pydantic import Field
from datetime import datetime

from pydantic import BaseModel


# Pydantic модель для создания пользователя
class UserCreate(BaseModel):
    username: str
    role_id: int = Field(..., ge=1)
    email: str
    phone_number: str
    password: str
    date_birth: datetime


# Pydantic модель для вывода пользователя
class UserOut(BaseModel):
    user_id: int
    username: str
    email: str
    phone_number: str
    date_birth: datetime

