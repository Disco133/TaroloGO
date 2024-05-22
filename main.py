from datetime import datetime
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
    date_birth: datetime


# Pydantic модель для вывода пользователя
class UserOut(BaseModel):
    user_id: int
    username: str
    email: str
    phone_number: str
    date_birth: datetime


class UserDateBirthUpdate(BaseModel):
    date_birth: datetime


class UserFirstNameUpdate(BaseModel):
    first_name: str


class UserSecondNameUpdate(BaseModel):
    second_name: str


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


#####   SERVICE_MODELS   #####


class ServiceCreate(BaseModel):
    service_name: str
    tarot_id: int = Field(..., ge=1)
    specialization_id: int = Field(..., ge=1)
    service_price: int


class ServiceOut(BaseModel):
    service_id: int
    service_name: str
    service_price: int


class ServiceNameUpdate(BaseModel):
    service_name: str


class ServicePriceUpdate(BaseModel):
    service_price: int


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
        password_hashed=hashed_password,
        date_birth=user.date_birth
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# создание юзера
@app.post("/users", response_model=UserOut)
async def create_user_endpoint(user: UserCreate, db: db_dependency):
    db_user = create_user(db, user)
    if db_user is None:
        raise HTTPException(status_code=400, detail="User creation failed")
    return db_user


# обновление имени в профиле
@app.post("/update_first_name/{user_id}", response_model=UserOut)
async def update_user_first_name(user_id: int, user_update: UserFirstNameUpdate, db: Session = Depends(get_db)):
    db_user = db.query(models.UserProfile).filter(models.UserProfile.user_id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db_user.first_name = user_update.first_name
    db.commit()
    db.refresh(db_user)
    return db_user


# обновление фамилии в профиле
@app.post("/update_second_name/{user_id}", response_model=UserOut)
async def update_user_second_name(user_id: int, user_update: UserSecondNameUpdate, db: Session = Depends(get_db)):
    db_user = db.query(models.UserProfile).filter(models.UserProfile.user_id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db_user.second_name = user_update.second_name
    db.commit()
    db.refresh(db_user)
    return db_user


# обновление даты рождения в профиле
@app.post("/update_date_birth/{user_id}", response_model=UserOut)
async def update_user_date_birth(user_id: int, user_update: UserDateBirthUpdate, db: Session = Depends(get_db)):
    db_user = db.query(models.UserProfile).filter(models.UserProfile.user_id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db_user.date_birth = user_update.date_birth
    db.commit()
    db.refresh(db_user)
    return db_user


# юзер по айди
@app.get("/users/{user_id}")
async def read_user(user_id: int, db: db_dependency):
    user = db.query(models.UserProfile).filter(models.UserProfile.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail='user is not found')
    return user


# функция для удаления юзера
def delete_user(db: Session, user_id: int):
    user = db.query(models.UserProfile).filter(models.UserProfile.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}


# удаление юзера
@app.delete("/users/{user_id}")
async def delete_user_endpoint(user_id: int, db: db_dependency):
    return delete_user(db, user_id)


###############################
#           service           #
###############################


# функция создания услуги
def create_service(db: Session, service: ServiceCreate):
    # Проверка, что пользователь с указанным tarot_id имеет роль таролога
    user = db.query(models.UserProfile).filter(models.UserProfile.user_id == service.tarot_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if user.role_id != 2:  # Предполагается, что role_id для таролога равен 1
        raise HTTPException(status_code=403, detail="User does not have the required role")

    db_service = models.Service(
        service_name=service.service_name,
        tarot_id=service.tarot_id,
        specialization_id=service.specialization_id,
        service_price=service.service_price
    )
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service


# создание услуги
@app.post('/service', response_model=ServiceOut)
async def create_service_endpoint(service: ServiceCreate, db: db_dependency):
    db_service = create_service(db, service)
    if db_service is None:
        raise HTTPException(status_code=400, detail="Service creation failed")
    return db_service


# обновление названия услуги
@app.post("/update_service_name/{service_id}", response_model=ServiceOut)
async def update_service_name(service_id: int, service_update: ServiceNameUpdate, db: Session = Depends(get_db)):
    db_service = db.query(models.Service).filter(models.Service.service_id == service_id).first()
    if db_service is None:
        raise HTTPException(status_code=404, detail="Service not found")

    db_service.service_name = service_update.service_name
    db.commit()
    db.refresh(db_service)
    return db_service


# обновление цены услуги
@app.post("/update_service_price/{service_id}", response_model=ServiceOut)
async def update_service_price(service_id: int, service_update: ServicePriceUpdate, db: Session = Depends(get_db)):
    db_service = db.query(models.Service).filter(models.Service.service_id == service_id).first()
    if db_service is None:
        raise HTTPException(status_code=404, detail="Service not found")

    db_service.service_price = service_update.service_price
    db.commit()
    db.refresh(db_service)
    return db_service


# услуга по айди
@app.get("/service/{service_id}")
async def read_service(service_id: int, db: db_dependency):
    service = db.query(models.Service).filter(models.Service.service_id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail='Role is not found')
    return service

# функция удаления услуги
def delete_service(db: Session, service_id: int):
    service_query = db.query(models.Service).filter(
        models.Service.service_id == service_id).first()
    if not service_query:
        raise HTTPException(status_code=404, detail="Service not found")
    db.delete(service_query)
    db.commit()
    return {"message": "Service deleted successfully"}

# удаление услуги
@app.delete("/service/{service_id}")
async def delete_service_endpoint(service_id: int, db: db_dependency):
    return delete_service(db, service_id)


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


# создание роли
@app.post("/role", response_model=RoleOut)
async def create_role_endpoint(role: RoleCreate, db: db_dependency):
    db_role = create_role(db, role)
    if db_role is None:
        raise HTTPException(status_code=400, detail="Role creation failed")
    return db_role


# название роли по её айди
@app.get("/role/{role_id}")
async def read_user(role_id: int, db: db_dependency):
    role_query = db.query(models.Role).filter(models.Role.role_id == role_id).first()
    if not role_query:
        raise HTTPException(status_code=404, detail='Role is not found')
    return role_query


# выводит всех юзеров по определённой роли
@app.get('/role_users/{role_id}')
async def read_users_by_role(role_id: int, db: db_dependency):
    read_role_query = (
        db.query(models.UserProfile).join(models.Role).filter(models.UserProfile.role_id == role_id).all())
    if not read_role_query:
        raise HTTPException(status_code=404, detail='Role is not found')
    users = [{'users_name': users.username} for users in read_role_query]
    return {'role_id': role_id, 'username': users}


# функция для удаления роли
def delete_role(db: Session, role_id: int):
    role_query = db.query(models.Role).filter(models.Role.role_id == role_id).first()
    if not role_query:
        raise HTTPException(status_code=404, detail="Role not found")
    db.delete(role_query)
    db.commit()
    return {"message": "Role deleted successfully"}


# удаление роли
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


# создания специализации
@app.post("/specialization", response_model=SpecOut)
async def create_specialization_endpoint(spec: SpecCreate, db: db_dependency):
    db_spec = create_specialization(db, spec)
    if db_spec is None:
        raise HTTPException(status_code=400, detail="Specialization creation failed")
    return db_spec


# название специализации по её айди
@app.get("/specialization/{specialization_id}")
async def read_specialization(specialization_id: int, db: db_dependency):
    specialization_query = db.query(models.Specialization).filter(
        models.Specialization.specialization_id == specialization_id).first()
    if not specialization_query:
        raise HTTPException(status_code=404, detail='Specialization is not found')
    return specialization_query


# функция для удаления специализации
def delete_specialization(db: Session, specialization_id: int):
    specialization_query = db.query(models.Specialization).filter(
        models.Specialization.specialization_id == specialization_id).first()
    if not specialization_query:
        raise HTTPException(status_code=404, detail="Specialization not found")
    db.delete(specialization_query)
    db.commit()
    return {"message": "Specialization deleted successfully"}


# удаление специализации
@app.delete("/specialization/{specialization_id}")
async def delete_specialization_endpoint(specialization_id: int, db: db_dependency):
    return delete_specialization(db, specialization_id)


###############################
#       spec_connection       #
###############################


# Функция для создания связи юзер - специализация
def create_specialization_bond(db: Session, spec_bond: UserSpecializationCreate):
    db_spec_bond = models.UserSpecialization(
        specialization_id=spec_bond.specialization_id,
        user_id=spec_bond.user_id
    )
    db.add(db_spec_bond)
    db.commit()
    db.refresh(db_spec_bond)
    return db_spec_bond


# связь юзер - специализация
@app.post("/specialization_bond", response_model=UserSpecializationOut)
async def create_specialization_endpoint(spec_bond: UserSpecializationCreate, db: db_dependency):
    db_spec_bond = create_specialization_bond(db, spec_bond)
    if db_spec_bond is None:
        raise HTTPException(status_code=400, detail="Specialization bond creation failed")
    return db_spec_bond


# выводит все специализации определённого юзера
@app.get("/user_specialization/{user_id}")
async def read_specialization_by_user(user_id: int, db: db_dependency):
    specialization_bond_query = (
        db.query(models.Specialization.specialization_name)
        .join(models.UserSpecialization,
              models.UserSpecialization.specialization_id == models.Specialization.specialization_id)
        .join(models.UserProfile, models.UserProfile.user_id == models.UserSpecialization.user_id)
        .filter(models.UserProfile.user_id == user_id)
        .all()
    )
    if not specialization_bond_query:
        raise HTTPException(status_code=404, detail='User is not found')
    specializations = [{"specialization_name": specialization.specialization_name} for specialization in
                       specialization_bond_query]
    return {"user_id": user_id, "specializations": specializations}


# выводит всех юзеров по определённой специализации
@app.get("/specialization_users/{specialization_id}")
async def read_users_by_specialization(specialization_id: int, db: db_dependency):
    specialization_bond_query = (
        db.query(models.UserProfile).join(models.UserSpecialization).join(models.Specialization)
        .filter(models.UserSpecialization.specialization_id == specialization_id).all())
    if not specialization_bond_query:
        raise HTTPException(status_code=404, detail='Specialization is not found')
    users = [{'users_name': users.username} for users in specialization_bond_query]
    return {"specialization_id": specialization_id, "usernames": users}


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
