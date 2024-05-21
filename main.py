from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from typing import Annotated
import models
import bcrypt

app = FastAPI()
models.Base.metadata.create_all(bind=engine)


 #####   USER_MODELS   #####


# Pydantic модель для создания пользователя
class UserCreate(BaseModel):
    username: str
    role_id: int = Field(..., ge=1)
    email: str
    phone_number: str
    password: str


# Pydantic модель для вывода пользователя
class UserOut(BaseModel):
    user_id: int
    username: str
    email: str
    phone_number: str


#####   ROLE_MODELS   #####


class RoleCreate(BaseModel):
    role_name: str


class RoleOut(BaseModel):
    role_id: int
    role_name: str


def get_db():
    db = SessionLocal()  # создаём сессию базы данных
    try:
        yield db  # возвращаем сессию для использования в маршрутах
    finally:
        db.close()  # закрываем сессию, когда она больше не нужна


db_dependency = Annotated[Session, Depends(get_db)]


###############################
#            user             #
###############################


# функция хеширования пароля
def hash_password(password: str) -> str:
    # Генерируем соль
    salt = bcrypt.gensalt()
    # Хешируем пароль с использованием соли
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')


# функция сверки пароля с его хеш версией
def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


# Функция для создания пользователя
def create_user(db: Session, user: UserCreate):
    # Здесь вы можете добавить логику хеширования пароля
    hashed_password = hash_password(user.password)
    db_user = models.UserProfile(
        username=user.username,
        role_id=user.role_id,
        email=user.email,
        phone_number=user.phone_number,
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


###############################
#            role             #
###############################


# Функция для создания пользователя
def create_role(db: Session, role: RoleCreate):
    # Здесь вы можете добавить логику хеширования пароля
    db_user = models.Role(
        role_name=role.role_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.post("/role", response_model=RoleOut)
async def create_role_endpoint(role: RoleCreate, db: db_dependency):
    db_user = create_role(db, role)
    if db_user is None:
        raise HTTPException(status_code=400, detail="Role creation failed")
    return db_user


@app.get("/role/{role_id}")
async def read_user(role_id: int, db: db_dependency):
    role_query = db.query(models.Role).filter(models.Role.role_id == role_id).first()
    if not role_query:
        raise HTTPException(status_code=404, detail='Role is not found')
    return role_query


def delete_role(db: Session, role_id: int):
    role_query = db.query(models.Role).filter(models.Role.role_id == role_id).first()
    if not role_query:
        raise HTTPException(status_code=404, detail="Role not found")
    db.delete(role_query)
    db.commit()
    return {"message": "User deleted successfully"}


@app.delete("/role/{role_id}")
async def delete_user_endpoint(role_id: int, db: db_dependency):
    return delete_role(db, role_id)
