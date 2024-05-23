from datetime import datetime
import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session, aliased
from sqlalchemy import update, alias
from sqlalchemy.sql import func
from database import SessionLocal, engine
from typing import Annotated, List
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


#####   SPEC_CONNECTION_MODELS   #####


class UserSpecializationCreate(BaseModel):
    specialization_id: int
    user_id: int


class UserSpecializationOut(BaseModel):
    user_specialization_id: int
    specialization_id: int
    user_id: int


#####   MESSAGE   #####


class MessageCreate(BaseModel):
    sender_id: int
    recipient_id: int
    message_text: str


class MessageRead(BaseModel):
    sender_id: int
    recipient_id: int
    message_date_read: datetime


class MessageOut(BaseModel):
    message_id: int
    sender_id: int
    recipient_id: int
    message_text: str
    message_date_send: datetime


class MessageResponse(BaseModel):
    message_text: str
    message_date_send: datetime
    is_read: bool


class MessagesResponse(BaseModel):
    sent_messages: List[MessageResponse]
    received_messages: List[MessageResponse]


#####   CONTACTS   #####



class ContactsInfo(BaseModel):
    username: str
    message_text: str
    message_date_send: datetime
    is_read: bool

class ContactsResponse(BaseModel):
    messages: List[ContactsInfo]


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
@app.post("/users/{user_id}/update_first_name/", response_model=UserOut)
def update_user_first_name(user_id: int, user_update: UserFirstNameUpdate, db: Session = Depends(get_db)):
    db_user = db.query(models.UserProfile).filter(models.UserProfile.user_id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db_user.first_name = user_update.first_name
    db.commit()
    db.refresh(db_user)
    return db_user


# обновление фамилии в профиле
@app.post("/users/{user_id}/update_second_name/", response_model=UserOut)
def update_user_second_name(user_id: int, user_update: UserSecondNameUpdate, db: Session = Depends(get_db)):
    db_user = db.query(models.UserProfile).filter(models.UserProfile.user_id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db_user.second_name = user_update.second_name
    db.commit()
    db.refresh(db_user)
    return db_user


# обновление даты рождения в профиле
@app.post("/users/{user_id}/update_date_birth/", response_model=UserOut)
def update_user_date_birth(user_id: int, user_update: UserDateBirthUpdate, db: Session = Depends(get_db)):
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


###############################
#           message           #
###############################


# функция для добавления контакта
def add_contact(db: Session, user_id: int, user_contact_id: int):
    contact_exists = db.query(models.Contacts).filter_by(user_id=user_id, user_contact_id=user_contact_id).first()
    if not contact_exists:
        db_contact = models.Contacts(
            user_id=user_id,
            user_contact_id=user_contact_id
        )
        db.add(db_contact)
        db.commit()
        db.refresh(db_contact)


# функция для создания нового сообщения
def create_message_for_db(db: Session, message: MessageCreate):
    db_message = models.Message(
        sender_id=message.sender_id,
        recipient_id=message.recipient_id,
        message_text=message.message_text
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)

    add_contact(db, message.sender_id, message.recipient_id)
    add_contact(db, message.recipient_id, message.sender_id)

    return db_message


# запрос для добавления сообщения в базу данных и генерации нового контакта
@app.post("/new_message", response_model=MessageOut)
async def create_message(message: MessageCreate, db: db_dependency):
    db_message = create_message_for_db(db, message)
    if db_message is None:
        raise HTTPException(status_code=400, detail="Message creation failed")
    return db_message

# запрос для помечания сообщения как прочитанного
@app.post("/message_read/{sender_id}/recipient/{recipient_id}", response_model=MessageRead)
async def message_read(sender_id: int, recipient_id: int, db: db_dependency):
    current_time = datetime.now()

    query = (
        update(models.Message)
        .filter(
            models.Message.sender_id == sender_id,
            models.Message.recipient_id == recipient_id,
            models.Message.message_date_read == None
        )
        .values(message_date_read=current_time)
        .execution_options(synchronize_session='fetch')
    )

    result = db.execute(query)
    db.commit()

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="No messages found to update")

    return MessageRead(message_date_read=current_time)


# функция для получения всей переписки между двумя пользователями
def get_messages_from_db(db: Session, sender_id: int, recipient_id: int):
    sent_messages = db.query(models.Message).filter(
        models.Message.sender_id == sender_id,
        models.Message.recipient_id == recipient_id
    ).all()

    received_messages = db.query(models.Message).filter(
        models.Message.sender_id == recipient_id,
        models.Message.recipient_id == sender_id
    ).all()

    if not sent_messages and not received_messages:
        raise HTTPException(status_code=404, detail="No messages found")

    return {
        "sent_messages": [
            MessageResponse(
                message_text=message.message_text,
                message_date_send=message.message_date_send,
                is_read=message.message_date_read is not None
            ) for message in sent_messages
        ],
        "received_messages": [
            MessageResponse(
                message_text=message.message_text,
                message_date_send=message.message_date_send,
                is_read=message.message_date_read is not None
            ) for message in received_messages
        ]
    }

# запрос для получения переписки между пользователями
@app.get("/messages/{sender_id}/recipient/{recipient_id}", response_model=MessagesResponse)
async def get_messages(sender_id: int, recipient_id: int, db: db_dependency):
    return get_messages_from_db(db, sender_id, recipient_id)

# функция для получения инфорциции (никнейма, последнего отправленного сообщения, даты и времени его отправки и статуса просмотра) каждого контакта для определенного пользователя
def get_last_messages_from_db(db: Session, user_id: int):
    sent_messages = aliased(models.Message)
    received_messages = aliased(models.Message)

    sent_subquery = (
        db.query(
            sent_messages.recipient_id.label('contact_id'),
            sent_messages.message_date_send.label('message_date_send'),
            sent_messages.message_id.label('message_id')
        )
        .filter(sent_messages.sender_id == user_id)
    )

    received_subquery = (
        db.query(
            received_messages.sender_id.label('contact_id'),
            received_messages.message_date_send.label('message_date_send'),
            received_messages.message_id.label('message_id')
        )
        .filter(received_messages.recipient_id == user_id)
    )

    union_subquery = sent_subquery.union_all(received_subquery).subquery()

    last_messages_subquery = (
        db.query(
            union_subquery.c.contact_id,
            func.max(union_subquery.c.message_date_send).label('last_date')
        )
        .group_by(union_subquery.c.contact_id)
        .subquery()
    )

    last_messages = (
        db.query(
            models.Message.message_id,
            models.Message.sender_id,
            models.Message.recipient_id,
            models.Message.message_text,
            models.Message.message_date_send,
            models.Message.message_date_read,
            models.UserProfile.username
        )
        .join(
            last_messages_subquery,
            (models.Message.message_date_send == last_messages_subquery.c.last_date) &
            ((models.Message.sender_id == last_messages_subquery.c.contact_id) |
             (models.Message.recipient_id == last_messages_subquery.c.contact_id))
        )
        .join(
            models.UserProfile,
            (models.UserProfile.user_id == models.Message.sender_id) |
            (models.UserProfile.user_id == models.Message.recipient_id)
        )
        .filter(
            (models.UserProfile.user_id != user_id)
        )
        .order_by(models.Message.message_date_send.desc())
        .all()
    )

    if not last_messages:
        raise HTTPException(status_code=404, detail="No messages found")

    return [
        ContactsInfo(
            username=message.username,
            message_text=message.message_text,
            message_date_send=message.message_date_send,
            is_read=message.message_date_read is not None
        )
        for message in last_messages
    ]

# запрос для получения никнейма, последнего отправленного сообщения, даты и времени его отправки и статуса просмотра каждого контакта для определенного пользователя
@app.get("/contacts/{user_id}", response_model=List[ContactsInfo])
async def get_last_message(user_id: int, db: Session = Depends(get_db)):
    return get_last_messages_from_db(db, user_id)

# функция для удаления сообщения
def delete_message_from_db(db: Session, sender_id: int, recipient_id: int, message_date_send: datetime):
    message_query = db.query(models.Message).filter(
        models.Message.sender_id == sender_id,
        models.Message.recipient_id == recipient_id,
        models.Message.message_date_send == message_date_send).first()
    if not message_query:
        raise HTTPException(status_code=404, detail="Message not found")
    db.delete(message_query)
    db.commit()
    return {"message": "Message deleted successfully"}


# запрос на удаление сообщения
@app.delete("/message_delete/{sender_id}/recipient_id/{recipient_id}/message_date_send/{message_date_send}")
async def delete_message(sender_id: int, recipient_id: int, message_date_send: datetime, db: db_dependency):
    return delete_message_from_db(db, sender_id, recipient_id, message_date_send)


# автоматический запуск uvicorn
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host='127.0.0.1',
        port=8000,
        reload=True
    )
