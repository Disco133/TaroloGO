import uvicorn
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


#####   SPEC_MODELS   #####


class SpecCreate(BaseModel):
    specialization_name: str


class SpecOut(BaseModel):
    specialization_id: int
    specialization_name: str


#####   SPEC_CONNECTION_MODELS   #####


class UserSpecializationCreate(BaseModel):
    specialization_id: int
    user_id: int


class UserSpecializationOut(BaseModel):
    user_specialization_id: int
    specialization_id: int
    user_id: int


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


# Функция для создания роли
def create_role(db: Session, role: RoleCreate):
    db_role = models.Role(
        role_name=role.role_name
    )
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role


@app.post("/role", response_model=RoleOut)
async def create_role_endpoint(role: RoleCreate, db: db_dependency):
    db_role = create_role(db, role)
    if db_role is None:
        raise HTTPException(status_code=400, detail="Role creation failed")
    return db_role


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
    return {"message": "Role deleted successfully"}


@app.delete("/role/{role_id}")
async def delete_user_endpoint(role_id: int, db: db_dependency):
    return delete_role(db, role_id)


###############################
#            spec             #
###############################


# Функция для создания специализации
def create_specialization(db: Session, spec: SpecCreate):
    db_spec = models.Specialization(
        specialization_name=spec.specialization_name
    )
    db.add(db_spec)
    db.commit()
    db.refresh(db_spec)
    return db_spec


@app.post("/specialization", response_model=SpecOut)
async def create_specialization_endpoint(spec: SpecCreate, db: db_dependency):
    db_spec = create_specialization(db, spec)
    if db_spec is None:
        raise HTTPException(status_code=400, detail="Specialization creation failed")
    return db_spec


@app.get("/specialization/{specialization_id}")
async def read_specialization(specialization_id: int, db: db_dependency):
    specialization_query = db.query(models.Specialization).filter(models.Specialization.specialization_id == specialization_id).first()
    if not specialization_query:
        raise HTTPException(status_code=404, detail='Specialization is not found')
    return specialization_query


def delete_specialization(db: Session, specialization_id: int):
    specialization_query = db.query(models.Specialization).filter(models.Specialization.specialization_id == specialization_id).first()
    if not specialization_query:
        raise HTTPException(status_code=404, detail="Specialization not found")
    db.delete(specialization_query)
    db.commit()
    return {"message": "Specialization deleted successfully"}


@app.delete("/specialization/{specialization_id}")
async def delete_specialization_endpoint(specialization_id: int, db: db_dependency):
    return delete_specialization(db, specialization_id)


###############################
#       spec_connection       #
###############################


# Функция для создания специализации
def create_specialization_bond(db: Session, spec_bond: UserSpecializationCreate):
    db_spec_bond = models.UserSpecialization(
        specialization_id=spec_bond.specialization_id,
        user_id=spec_bond.user_id
    )
    db.add(db_spec_bond)
    db.commit()
    db.refresh(db_spec_bond)
    return db_spec_bond


@app.post("/specialization_bond", response_model=UserSpecializationOut)
async def create_specialization_endpoint(spec_bond: UserSpecializationCreate, db: db_dependency):
    db_spec_bond = create_specialization_bond(db, spec_bond)
    if db_spec_bond is None:
        raise HTTPException(status_code=400, detail="Specialization bond creation failed")
    return db_spec_bond


@app.get("/user_specialization/{user_id}")
async def read_specialization_by_user(user_id: int, db: db_dependency):
    specialization_bond_query = (db.query(models.Specialization).join(models.UserSpecialization).join(models.UserProfile)
                            .filter(models.UserSpecialization.user_id == user_id).first())
    if not specialization_bond_query:
        raise HTTPException(status_code=404, detail='User is not found')
    return specialization_bond_query


@app.get("/specialization_users/{specialization_id}")
async def read_users_by_specialization(specialization_id: int, db: db_dependency):
    specialization_bond_query = (db.query(models.UserProfile).join(models.UserSpecialization).join(models.Specialization)
                            .filter(models.UserSpecialization.specialization_id == specialization_id).first())
    if not specialization_bond_query:
        raise HTTPException(status_code=404, detail='Specialization is not found')
    return specialization_bond_query


def delete_users_specialization(db: Session, user_id: int, specialization_id: int):
    user_specialization_query = db.query(models.UserSpecialization).filter(
        models.UserSpecialization.user_id == user_id,
        models.UserSpecialization.specialization_id == specialization_id)
    user_specialization_query = user_specialization_query.first()
    if not user_specialization_query:
        raise HTTPException(status_code=404, detail="User/Specialization not found")
    db.delete(user_specialization_query)
    db.commit()
    return {"message": "User's specialization deleted successfully"}


@app.delete("/users/{user_id}/specialization/{specialization_id}")
async def delete_user_specialization_endpoint(user_id: int, specialization_id: int, db: db_dependency):
    return delete_users_specialization(db, user_id, specialization_id)


# автоматический запуск uvicorn
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host='127.0.0.1',
        port=8000,
        reload=True
    )
