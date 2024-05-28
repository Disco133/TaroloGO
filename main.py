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


class TarotSpecializationCreate(BaseModel):
    specialization_id: int
    tarot_id: int


class TarotSpecializationOut(BaseModel):
    tarot_specialization_id: int
    specialization_id: int
    tarot_id: int


#####   MESSAGE_MODELS   #####


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


#####   CONTACTS_MODELS   #####


class ContactsInfo(BaseModel):
    username: str
    message_text: str
    message_date_send: datetime
    is_read: bool


class ContactsResponse(BaseModel):
    messages: List[ContactsInfo]


#####   USER_FAVORITE_TAROTS_MODELS    #####

class UserFavoriteTarotsCreate(BaseModel):
    user_id: int
    tarot_id: int


class UserFavoriteTarotsOut(BaseModel):
    favorite_tarot_id: int
    user_id: int
    tarot_id: int


#####   STATUS_MODELS    #####


class StatusCreate(BaseModel):
    status_name: str


class StatusOut(BaseModel):
    status_id: int
    status_name: str


#####   USER_SERVICE_HISTORY_MODELS    #####


class UserServiceHistoryCreate(BaseModel):
    user_id: int
    service_id: int
    status_id: int


class UserServiceHistoryOut(BaseModel):
    history_id: int
    user_id: int
    service_id: int
    status_id: int


class UserServiceHistoryUpdateReview(BaseModel):
    history_id: int
    review_title: str
    review_text: str
    review_value: int = Field(..., le=5, ge=1)
    review_date_time: datetime


#####   NOTIFICATIONS_MODELS    #####


class SystemNotificationCreate(BaseModel):
    notification_status_id: int
    notification_type_id: int
    notification_title: str
    notification_text: str
    notification_date_time: datetime


class SystemNotificationOut(BaseModel):
    notification_id: int
    notification_status_id: int
    notification_type_id: int
    notification_title: str
    notification_text: str
    notification_date_time: datetime


class NotificationStatusCreate(BaseModel):
    notification_status_name: str


class NotificationTypeCreate(BaseModel):
    notification_type_name: str


class NotificationStatusOut(BaseModel):
    notification_status_id: int
    notification_status_name: str


class NotificationTypeOut(BaseModel):
    notification_type_id: int
    notification_type_name: str


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


# обновление статуса is_delete
@app.post("/update_user_is_deleted/{user_id}")
async def update_user_is_deleted(user_id: int, is_deleted: bool, db: db_dependency):
    db_user = db.query(models.UserProfile).filter(models.UserProfile.user_id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db_user.is_deleted = is_deleted
    db.commit()
    db.refresh(db_user)
    return {"message": "User is_deleted updated successfully"}


# обновление имени в профиле
@app.post("/update_first_name/{user_id}")
async def update_user_first_name(user_id: int, first_name: str, db: db_dependency):
    db_user = db.query(models.UserProfile).filter(models.UserProfile.user_id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db_user.first_name = first_name
    db.commit()
    db.refresh(db_user)
    return {"message": "User first_name updated successfully"}


# обновление фамилии в профиле
@app.post("/update_second_name/{user_id}")
async def update_user_second_name(user_id: int, second_name: str, db: db_dependency):
    db_user = db.query(models.UserProfile).filter(models.UserProfile.user_id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db_user.second_name = second_name
    db.commit()
    db.refresh(db_user)
    return {"message": "User second_name updated successfully"}


# обновление даты рождения в профиле
@app.post("/update_date_birth/{user_id}")
async def update_date_birth(user_id: int, date_birth: datetime, db: db_dependency):
    db_user = db.query(models.UserProfile).filter(models.UserProfile.user_id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db_user.date_birth = date_birth
    db.commit()
    db.refresh(db_user)
    return {"message": "User date_birth updated successfully"}


# обновление описания таролога
@app.post("/update_user_description/{user_id}")
async def update_user_description(user_id: int, user_description: str, db: db_dependency):
    db_user = db.query(models.UserProfile).filter(models.UserProfile.user_id == user_id).first()
    db_user.user_description = user_description
    db.commit()
    db.refresh(db_user)
    return {"message": "User description updated successfully"}


# обновление опыта работы таролога
@app.post("/update_tarot_experience/{user_id}")
async def update_tarot_experience(user_id: int, tarot_experience: float, db: db_dependency):
    db_user = db.query(models.UserProfile).filter(models.UserProfile.user_id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if db_user.role_id != 1:  # Предполагается, что role_id для таролога равен 1
        raise HTTPException(status_code=403, detail="User does not have the required role")
    db_user.tarot_experience = tarot_experience
    db.commit()
    db.refresh(db_user)
    return {"message": "User tarot_experience updated successfully"}


# юзер по айди
@app.get("/users/{user_id}")
async def read_user(user_id: int, db: db_dependency):
    db_user = db.query(models.UserProfile).filter(models.UserProfile.user_id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail='User is not found')
    return db_user


# функция для удаления юзера
def delete_user(db: Session, user_id: int):
    db_user = db.query(models.UserProfile).filter(models.UserProfile.user_id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
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
    db_user = db.query(models.UserProfile).filter(models.UserProfile.user_id == service.tarot_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if db_user.role_id != 1:  # Предполагается, что role_id для таролога равен 1
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
async def update_service_name(service_id: int, service_update: ServiceNameUpdate, db: db_dependency):
    db_service = db.query(models.Service).filter(models.Service.service_id == service_id).first()
    if db_service is None:
        raise HTTPException(status_code=404, detail="Service not found")

    db_service.service_name = service_update.service_name
    db.commit()
    db.refresh(db_service)
    return db_service


# обновление цены услуги
@app.post("/update_service_price/{service_id}", response_model=ServiceOut)
async def update_service_price(service_id: int, service_update: ServicePriceUpdate, db: db_dependency):
    db_service = db.query(models.Service).filter(models.Service.service_id == service_id).first()
    if db_service is None:
        raise HTTPException(status_code=404, detail="Service not found")

    db_service.service_price = service_update.service_price
    db.commit()
    db.refresh(db_service)
    return db_service


# обновление описания услуги
@app.post("/update_service_description/{service_id}")
async def update_service_description(service_id: int, service_description: str, db: db_dependency):
    db_service = db.query(models.Service).filter(models.Service.service_id == service_id).first()
    if db_service is None:
        raise HTTPException(status_code=404, detail="Service not found")

    db_service.service_description = service_description
    db.commit()
    db.refresh(db_service)
    return {"message": "Service description updated successfully"}


# услуга по айди
@app.get("/service/{service_id}")
async def read_service(service_id: int, db: db_dependency):
    db_service = db.query(models.Service).filter(models.Service.service_id == service_id).first()
    if not db_service:
        raise HTTPException(status_code=404, detail='Role is not found')
    return db_service


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


# Функция для создания связи таролог - специализация
def create_specialization_bond(db: Session, spec_bond: TarotSpecializationCreate):
    db_user = db.query(models.UserProfile).filter(models.UserProfile.user_id == spec_bond.tarot_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if db_user.role_id != 1:  # Предполагается, что role_id для таролога равен 1
        raise HTTPException(status_code=403, detail="User does not have the required role")
    db_spec_bond = models.TarotSpecialization(
        specialization_id=spec_bond.specialization_id,
        tarot_id=spec_bond.tarot_id
    )
    db.add(db_spec_bond)
    db.commit()
    db.refresh(db_spec_bond)
    return db_spec_bond


# таблица связи юзер-специализация
@app.post("/specialization_bond", response_model=TarotSpecializationOut)
async def create_specialization_endpoint(spec_bond: TarotSpecializationCreate, db: db_dependency):
    db_spec_bond = create_specialization_bond(db, spec_bond)
    if db_spec_bond is None:
        raise HTTPException(status_code=400, detail="Specialization bond creation failed")
    return db_spec_bond


# выводит все специализации определённого таролога
@app.get("/tarot_specialization/{tarot_id}")
async def read_specialization_by_tarot(tarot_id: int, db: db_dependency):
    specialization_bond_query = (
        db.query(models.Specialization.specialization_name)
        .join(models.TarotSpecialization,
              models.TarotSpecialization.specialization_id == models.Specialization.specialization_id)
        .join(models.UserProfile, models.UserProfile.user_id == models.TarotSpecialization.tarot_id)
        .filter(models.UserProfile.user_id == tarot_id)
        .all()
    )
    if not specialization_bond_query:
        raise HTTPException(status_code=404, detail='Tarot is not found')
    specializations = [{"specialization_name": specialization.specialization_name} for specialization in
                       specialization_bond_query]
    return {"tarot_id": tarot_id, "specializations": specializations}


# выводит всех тарологов по определённой специализации
@app.get("/specialization_tarot/{specialization_id}")
async def read_tarot_by_specialization(specialization_id: int, db: db_dependency):
    specialization_bond_query = (
        db.query(models.UserProfile).join(models.TarotSpecialization).join(models.Specialization)
        .filter(models.TarotSpecialization.specialization_id == specialization_id).all())
    if not specialization_bond_query:
        raise HTTPException(status_code=404, detail='Specialization is not found')
    tarots = [{'tarots_name': tarots.username} for tarots in specialization_bond_query]
    return {"specialization_id": specialization_id, "usernames": tarots}


# функция удаления связи таролог-специализация
def delete_tarots_specialization(db: Session, tarot_id: int, specialization_id: int):
    tarot_specialization_query = db.query(models.TarotSpecialization).filter(
        models.TarotSpecialization.tarot_id == tarot_id,
        models.TarotSpecialization.specialization_id == specialization_id)
    tarot_specialization_query = tarot_specialization_query.first()
    if not tarot_specialization_query:
        raise HTTPException(status_code=404, detail="Tarot/Specialization not found")
    db.delete(tarot_specialization_query)
    db.commit()
    return {"message": "Tarot's specialization deleted successfully"}


# удаление связи таролог-специализация
@app.delete("/tarots/{tarot_id}/specialization/{specialization_id}")
async def delete_tarot_specialization_endpoint(tarot_id: int, specialization_id: int, db: db_dependency):
    return delete_tarots_specialization(db, tarot_id, specialization_id)


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


###############################
#          Favorite           #
###############################


# функция добавление таролога в избранные
def create_user_favorite_tarot(db: Session, favorite: UserFavoriteTarotsCreate):
    db_favorite = models.UserFavoriteTarots(
        user_id=favorite.user_id,
        tarot_id=favorite.tarot_id
    )
    db.add(db_favorite)
    db.commit()
    db.refresh(db_favorite)
    return db_favorite


# добавление таролога в избранные
@app.post("/user_favorite_tarot", response_model=UserFavoriteTarotsOut)
async def create_user_favorite_tarot_endpoint(favorite: UserFavoriteTarotsCreate, db: db_dependency):
    db_favorite = create_user_favorite_tarot(db, favorite)
    if db_favorite is None:
        raise HTTPException(status_code=400, detail="Role creation failed")
    return db_favorite


# функция получения всех тарологов в избранных у пользователя
def get_user_favorite_tarots(db: Session, user_id: int):
    return db.query(models.UserFavoriteTarots).filter(models.UserFavoriteTarots.user_id == user_id).all()


# получение всех тарологов в избранных у пользователя
@app.get('/user_favorite_tarot/{user_id}', response_model=List[UserFavoriteTarotsOut])
async def read_user_favorite_tarots(user_id: int, db: db_dependency):
    favorites = get_user_favorite_tarots(db, user_id)
    if not favorites:
        raise HTTPException(status_code=404, detail="No favorites found for this user")
    return favorites


# функция для удаления таролога из избранных
def delete_user_favorite_tarot(db: Session, user_id: int, tarot_id: int):
    favorite_query = db.query(models.UserFavoriteTarots).filter(
        models.UserFavoriteTarots.user_id == user_id,
        models.UserFavoriteTarots.user_id == user_id)
    favorite_query = favorite_query.first()
    if not favorite_query:
        raise HTTPException(status_code=404, detail="Favorite not found")
    db.delete(favorite_query)
    db.commit()
    return {"message": "Favorite tarot deleted successfully"}


# удаление таролога из избранных
@app.delete("/users_favorite_tarot/{user_id}/{tarot_id}")
async def delete_user_favorite_tarot_endpoint(user_id: int, tarot_id: int, db: db_dependency):
    return delete_user_favorite_tarot(db, user_id, tarot_id)


###############################
#            Status           #
###############################

# функция для создания статуса
def create_status(db: Session, stat: StatusCreate):
    db_stat = models.Status(
        status_name=stat.status_name
    )
    db.add(db_stat)
    db.commit()
    db.refresh(db_stat)
    return db_stat


# создание статуса
@app.post("/status", response_model=StatusOut)
async def create_status_endpoint(stat: StatusCreate, db: db_dependency):
    db_status = create_status(db, stat)
    if db_status is None:
        raise HTTPException(status_code=400, detail="Status creation failed")
    return db_status


# название статуса по его айди
@app.get("/status/{status_id}")
async def read_status(status_id: int, db: db_dependency):
    status_query = db.query(models.Status).filter(models.Status.status_id == status_id).first()
    if not status_query:
        raise HTTPException(status_code=404, detail='Status is not found')
    return status_query


# функция для удаления статуса
def delete_status(db: Session, status_id: int):
    status_query = db.query(models.Status).filter(models.Status.status_id == status_id).first()
    if not status_query:
        raise HTTPException(status_code=404, detail="Status not found")
    db.delete(status_query)
    db.commit()
    return {"message": "Status deleted successfully"}


# удаление статуса
@app.delete("/delete_status/{status_id}")
async def delete_status_endpoint(status_id: int, db: db_dependency):
    return delete_status(db, status_id)


###############################
#      UserServiceHistory     #
###############################


# функция создание истории
def create_history(db: Session, history: UserServiceHistoryCreate): \
        # Поиск службы по service_id
    service = db.query(models.Service).filter(models.Service.service_id == history.service_id).first()

    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    db_history = models.UserServiceHistory(
        user_id=history.user_id,
        service_id=history.service_id,
        tarot_id=service.tarot_id,
        status_id=history.status_id
    )
    db.add(db_history)
    db.commit()
    db.refresh(db_history)
    return db_history


# создание истории
@app.post("/history", response_model=UserServiceHistoryOut)
async def create_user_endpoint(history: UserServiceHistoryCreate, db: db_dependency):
    db_history = create_history(db, history)
    if db_history is None:
        raise HTTPException(status_code=400, detail="History creation failed")
    return db_history


# функция обновления отзыва
def update_review(db: Session, history_update: UserServiceHistoryUpdateReview):
    db_history = db.query(models.UserServiceHistory).filter(
        models.UserServiceHistory.history_id == history_update.history_id).first()

    if not db_history:
        raise HTTPException(status_code=404, detail="History record not found")

    old_review_value = db_history.review_value
    db_history.review_title = history_update.review_title
    db_history.review_text = history_update.review_text
    db_history.review_value = history_update.review_value
    db_history.review_date_time = datetime.utcnow()

    tarot_id = db_history.tarot_id
    update_tarot_rating(db, tarot_id, old_review_value, history_update.review_value)

    db.commit()
    db.refresh(db_history)

    return db_history


# функция обновления рейтинга таролога при добавлении новой оценки
def update_tarot_rating(db: Session, tarot_id: int, old_review_value: int, new_review_value: int):
    tarot_profile = db.query(models.UserProfile).filter(models.UserProfile.user_id == tarot_id).first()

    if not tarot_profile:
        raise HTTPException(status_code=404, detail="Tarot profile not found")

    # Получаем текущие значения средней оценки и количество отзывов с review_value != 0
    current_reviews_query = db.query(models.UserServiceHistory).filter(
        models.UserServiceHistory.tarot_id == tarot_id,
        models.UserServiceHistory.review_value != 0
    )

    current_reviews_count = current_reviews_query.count()
    print(current_reviews_count)
    if current_reviews_count == 0:
        tarot_profile.tarot_rating = new_review_value if new_review_value != 0 else None
    else:
        # Пересчитываем сумму всех отзывов с review_value != 0
        current_reviews_sum = sum(review.review_value for review in current_reviews_query.all())

        # Обновляем сумму с учетом нового и старого значения review_value
        new_reviews_sum = current_reviews_sum - old_review_value + new_review_value

        # Пересчитываем среднюю оценку
        new_rating = new_reviews_sum / (current_reviews_count + 1)

        # Обновляем среднюю оценку таролога в таблице UserProfile
        tarot_profile.tarot_rating = new_rating

    db.commit()


# обновление отзыва
@app.post("/update_review/{history_id}", response_model=UserServiceHistoryOut)
async def update_review_endpoint(history_update: UserServiceHistoryUpdateReview, db: db_dependency):
    updated_history = update_review(db, history_update)
    return updated_history


# обновление статуса услуги
@app.post("/update_service_status/{history_id}")
async def update_service_status(history_id: int, status_id: int, db: db_dependency):
    db_history = db.query(models.UserServiceHistory).filter(models.UserServiceHistory.history_id == history_id).first()
    if db_history is None:
        raise HTTPException(status_code=404, detail="History record not found")
    db_service_status = db.query(models.Status).filter(
        models.Status.status_id == status_id).first()
    if db_service_status is None:
        raise HTTPException(status_code=404, detail="Status not found")
    db_history.status_id = status_id
    db.commit()
    db.refresh(db_service_status)
    return {"message": "Status updated successfully"}


# вывод user_service_history
@app.get("/user_service_history/{history_id}")
async def read_user_service_history(history_id: int, db: db_dependency):
    history_query = db.query(models.UserServiceHistory).filter(
        models.UserServiceHistory.history_id == history_id).first()
    if not history_query:
        raise HTTPException(status_code=404, detail='History is not found')
    return history_query


###############################
#       Notification_st       #
###############################


# функция для создания статуса уведомления
def create_notification_status(db: Session, stat: NotificationStatusCreate):
    db_stat = models.NotificationStatus(
        notification_status_name=stat.notification_status_name
    )
    db.add(db_stat)
    db.commit()
    db.refresh(db_stat)
    return db_stat


# создание статуса уведомления
@app.post("/notification_status", response_model=NotificationStatusOut)
async def create_notification_status_endpoint(stat: NotificationStatusCreate, db: db_dependency):
    db_status = create_notification_status(db, stat)
    if db_status is None:
        raise HTTPException(status_code=400, detail="Notification status creation failed")
    return db_status


# название статуса уведомления по его айди
@app.get("/notification_status/{notification_status_id}")
async def read_notification_status(notification_status_id: int, db: db_dependency):
    notification_status_query = db.query(models.NotificationStatus).filter(
        models.NotificationStatus.notification_status_id == notification_status_id).first()
    if not notification_status_query:
        raise HTTPException(status_code=404, detail='Notification Status is not found')
    return notification_status_query


# функция для удаления статуса уведомления
def delete_notification_status(db: Session, notification_status_id: int):
    notification_status_query = db.query(models.NotificationStatus).filter(
        models.NotificationStatus.notification_status_id == notification_status_id).first()
    if not notification_status_query:
        raise HTTPException(status_code=404, detail="Notification status not found")
    db.delete(notification_status_query)
    db.commit()
    return {"message": "Notification status deleted successfully"}


# удаление статуса уведомления
@app.delete("/delete_notification_status/{notification_status_id}")
async def delete_notification_status_endpoint(notification_status_id: int, db: db_dependency):
    return delete_notification_status(db, notification_status_id)


###############################
#      Notification_type      #
###############################


# функция для создания типа уведомления
def create_notification_type(db: Session, n_type: NotificationTypeCreate):
    db_type = models.NotificationType(
        notification_type_name=n_type.notification_type_name
    )
    db.add(db_type)
    db.commit()
    db.refresh(db_type)
    return db_type


# создание типа уведомления
@app.post("/notification_type", response_model=NotificationTypeOut)
async def create_notification_type_endpoint(n_type: NotificationTypeCreate, db: db_dependency):
    db_type = create_notification_type(db, n_type)
    if db_type is None:
        raise HTTPException(status_code=400, detail="Notification type creation failed")
    return db_type


# название типа уведомления по его айди
@app.get("/notification_type/{notification_type_id}")
async def read_notification_status(notification_type_id: int, db: db_dependency):
    notification_type_query = db.query(models.NotificationType).filter(
        models.NotificationType.notification_type_id == notification_type_id).first()
    if not notification_type_query:
        raise HTTPException(status_code=404, detail='Notification type is not found')
    return notification_type_query


# функция для удаления типа уведомления
def delete_notification_type(db: Session, notification_type_id: int):
    notification_type_query = db.query(models.NotificationType).filter(
        models.NotificationType.notification_type_id == notification_type_id).first()
    if not notification_type_query:
        raise HTTPException(status_code=404, detail="Notification type not found")
    db.delete(notification_type_query)
    db.commit()
    return {"message": "Notification type deleted successfully"}


# удаление типа уведомления
@app.delete("/delete_type/{notification_type_id}")
async def delete_notification_type_endpoint(notification_type_id: int, db: db_dependency):
    return delete_notification_type(db, notification_type_id)


###############################
#     System_notification     #
###############################


# функция для создания уведомления
def create_notification(db: Session, notification: SystemNotificationCreate):
    db_notification = models.SystemNotification(
        notification_status_id=notification.notification_status_id,
        notification_type_id=notification.notification_type_id,
        notification_title=notification.notification_title,
        notification_text=notification.notification_text,
        notification_date_time=notification.notification_date_time
    )
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification


# создание уведомления
@app.post("/notification", response_model=SystemNotificationOut)
async def create_notification_endpoint(notification: SystemNotificationCreate, db: db_dependency):
    db_notification = create_notification(db, notification)
    if db_notification is None:
        raise HTTPException(status_code=400, detail="Notification creation failed")
    return db_notification


# название уведомления по его айди
@app.get("/notification/{notification_id}")
async def read_notification(notification_id: int, db: db_dependency):
    notification_query = db.query(models.SystemNotification).filter(
        models.SystemNotification.notification_id == notification_id).first()
    if not notification_query:
        raise HTTPException(status_code=404, detail='Notification is not found')
    return notification_query


# функция для удаления Уведомления
def delete_notification(db: Session, notification_id: int):
    notification_query = db.query(models.SystemNotification).filter(
        models.SystemNotification.notification_id == notification_id).first()
    if not notification_query:
        raise HTTPException(status_code=404, detail="Notification not found")
    db.delete(notification_query)
    db.commit()
    return {"message": "Notification deleted successfully"}


# удаление уведомления
@app.delete("/delete_notification/{notification_id}")
async def delete_notification_endpoint(notification_id: int, db: db_dependency):
    return delete_notification(db, notification_id)


# автоматический запуск uvicorn
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host='127.0.0.1',
        port=8000,
        reload=True
    )
