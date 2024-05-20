from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from typing import Annotated
import models

app = FastAPI()
models.Base.metadata.create_all(bind=engine)


# Pydantic модель для создания пользователя
class UserCreate(BaseModel):
    username: str
    email: str
    password: str


# Pydantic модель для вывода пользователя
class UserOut(BaseModel):
    user_id: int
    username: str
    email: str

    # Позволяет Pydantic работать с ORM объектами
    # class Config:
    #     orm_mode = True


def get_db():
    db = SessionLocal()  # создаём сессию базы данных
    try:
        yield db  # возвращаем сессию для использования в маршрутах
    finally:
        db.close()  # закрываем сессию, когда она больше не нужна


db_dependency = Annotated[Session, Depends(get_db)]


# Функция для создания пользователя
def create_user(db: Session, user: UserCreate):
    # Здесь вы можете добавить логику хеширования пароля
    hashed_password = user.password
    db_user = models.UserProfile(
        username=user.username,
        email=user.email,
        password_hashed=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.post("/users", response_model=UserOut)
async def create_user_endpoint(user: UserCreate, db: db_dependency):
    db_user = create_user(db, user)
    if db_user is None:
        raise HTTPException(status_code=400, detail="User creation failed")
    return db_user


@app.get("/users/{user_id}")
async def read_user(user_id: int, db: db_dependency):
    user = db.query(models.UserProfile).filter(models.UserProfile.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail='user is not found')
    return user


def delete_user(db: Session, user_id: int):
    user = db.query(models.UserProfile).filter(models.UserProfile.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}


@app.delete("/users/{user_id}")
async def delete_user_endpoint(user_id: int, db: db_dependency):
    return delete_user(db, user_id)
