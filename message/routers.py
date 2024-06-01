from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.orm import aliased

from user.models import UserProfile
from message.schemas import MessageOut, MessageCreate, ContactsInfo
from message.models import Message, Contacts
from database import get_session
from sqlalchemy.ext.asyncio import AsyncSession



router = APIRouter(
    prefix='/message',
    tags=['Message/Contacts']
)


# функция для добавления контакта
async def add_contact(user_id: int, user_contact_id: int, session: AsyncSession = Depends(get_session)):
    contact_exists_ = await session.execute(select(Contacts).filter_by(user_id=user_id, user_contact_id=user_contact_id))
    contact_exists = contact_exists_.scalars().first()
    if not contact_exists:
        db_contact = Contacts(
            user_id=user_id,
            user_contact_id=user_contact_id
        )
        session.add(db_contact)
        await session.commit()
        await session.refresh(db_contact)


# функция для создания нового сообщения
async def create_message_for_db(message: MessageCreate, session: AsyncSession = Depends(get_session)):
    db_message = Message(
        sender_id=message.sender_id,
        recipient_id=message.recipient_id,
        message_text=message.message_text
    )
    session.add(db_message)
    await session.commit()
    await session.refresh(db_message)
    await add_contact(message.sender_id, message.recipient_id, session)
    await add_contact(message.recipient_id, message.sender_id, session)
    return db_message


# запрос для добавления сообщения в базу данных и генерации нового контакта
@router.post("/create", response_model=MessageOut)
async def create_message(message: MessageCreate, session: AsyncSession = Depends(get_session)):
    db_message = await create_message_for_db(message, session)
    if db_message is None:
        raise HTTPException(status_code=400, detail="Message creation failed")
    return db_message


# Функция для получения всей переписки между двумя пользователями
async def get_messages_from_db(sender_id: int, recipient_id: int, session: AsyncSession = Depends(get_session)):
    # Асинхронный запрос для отправленных сообщений
    sent_messages_query = select(Message).filter(
        Message.sender_id == sender_id,
        Message.recipient_id == recipient_id
    )
    sent_messages_result = await session.execute(sent_messages_query)
    sent_messages = sent_messages_result.scalars().all()

    # Асинхронный запрос для полученных сообщений
    received_messages_query = select(Message).filter(
        Message.sender_id == recipient_id,
        Message.recipient_id == sender_id
    )
    received_messages_result = await session.execute(received_messages_query)
    received_messages = received_messages_result.scalars().all()

    # Объединение отправленных и полученных сообщений
    all_messages = sent_messages + received_messages

    # Сортировка сообщений по дате отправки
    all_messages.sort(key=lambda msg: msg.message_date_send)

    if not all_messages:
        raise HTTPException(status_code=404, detail="No messages found")

    return [
        MessageOut(
            message_id=message.message_id,
            sender_id=message.sender_id,
            recipient_id=message.recipient_id,
            message_text=message.message_text,
            message_date_send=message.message_date_send
        ) for message in all_messages
    ]


# запрос для получения переписки между пользователями
@router.get("/show_chat/{sender_id}/recipient/{recipient_id}", response_model=List[MessageOut])
async def get_messages(sender_id: int, recipient_id: int, session: AsyncSession = Depends(get_session)):
    return await get_messages_from_db(sender_id, recipient_id, session)


async def get_last_messages_from_db(user_id: int, session: AsyncSession = Depends(get_session)):
    sent_messages = aliased(Message)
    received_messages = aliased(Message)

    sent_subquery = (
        select(
            sent_messages.recipient_id.label('contact_id'),
            sent_messages.message_date_send.label('message_date_send'),
            sent_messages.message_id.label('message_id'),
            sent_messages.sender_id.label('sender_id')
        )
        .filter(sent_messages.sender_id == user_id)
    )

    received_subquery = (
        select(
            received_messages.sender_id.label('contact_id'),
            received_messages.message_date_send.label('message_date_send'),
            received_messages.message_id.label('message_id'),
            received_messages.sender_id.label('sender_id')
        )
        .filter(received_messages.recipient_id == user_id)
    )

    union_subquery = sent_subquery.union_all(received_subquery).subquery()

    last_messages_subquery = (
        select(
            union_subquery.c.contact_id,
            func.max(union_subquery.c.message_date_send).label('last_date')
        )
        .group_by(union_subquery.c.contact_id)
    ).subquery()

    last_messages_query = (
        select(
            Message.message_id,
            Message.sender_id,
            Message.recipient_id,
            Message.message_text,
            Message.message_date_send,
            UserProfile.user_id.label('companion_id'),
            UserProfile.username,
            UserProfile.first_name,
            UserProfile.second_name
        )
        .join(
            last_messages_subquery,
            (Message.message_date_send == last_messages_subquery.c.last_date) &
            ((Message.sender_id == last_messages_subquery.c.contact_id) |
             (Message.recipient_id == last_messages_subquery.c.contact_id))
        )
        .join(
            UserProfile,
            (UserProfile.user_id == Message.sender_id) |
            (UserProfile.user_id == Message.recipient_id)
        )
        .filter(
            (UserProfile.user_id != user_id)
        )
        .order_by(Message.message_date_send.desc())
    )

    result = await session.execute(last_messages_query)
    last_messages = result.fetchall()

    if not last_messages:
        raise HTTPException(status_code=404, detail="No messages found")

    # Словарь для хранения последних сообщений для каждого контакта
    last_messages_dict = {}

    # Поиск самого последнего сообщения для каждого контакта
    for message in last_messages:
        contact_id = message.companion_id
        if contact_id not in last_messages_dict:
            last_messages_dict[contact_id] = message
        else:
            # Если сообщение уже есть, сравниваем даты и обновляем, если это более позднее сообщение
            if message.message_date_send > last_messages_dict[contact_id].message_date_send:
                last_messages_dict[contact_id] = message

    # Возвращаем только последние сообщения для каждого контакта
    return [
        ContactsInfo(
            companion_id=message.companion_id,
            username=message.username,
            first_name=message.first_name,
            second_name=message.second_name,
            sender_id=message.sender_id,
            message_text=message.message_text,
            message_date_send=message.message_date_send,
        )
        for message in last_messages_dict.values()
    ]



# запрос для получения никнейма, последнего отправленного сообщения, даты и времени его отправки и статуса просмотра каждого контакта для определенного пользователя
@router.get("/contacts_info/{user_id}", response_model=List[ContactsInfo])
async def get_last_message(user_id: int, session: AsyncSession = Depends(get_session)):
    return await get_last_messages_from_db(user_id, session)



# Асинхронная функция для удаления сообщения
async def delete_message_from_db(db: AsyncSession, sender_id: int, recipient_id: int, message_date_send: datetime):
    # Асинхронный запрос для поиска сообщения
    message_query = await db.execute(
        select(Message).filter(
            Message.sender_id == sender_id,
            Message.recipient_id == recipient_id,
            Message.message_date_send == message_date_send
        )
    )
    message = message_query.scalar_one_or_none()

    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    await db.delete(message)
    await db.commit()
    return {"message": "Message deleted successfully"}

# Запрос на удаление сообщения
@router.delete("/message_delete/{sender_id}/recipient_id/{recipient_id}/message_date_send/{message_date_send}")
async def delete_message(sender_id: int, recipient_id: int, message_date_send: datetime, db: AsyncSession = Depends(get_session)):
    return await delete_message_from_db(db, sender_id, recipient_id, message_date_send)