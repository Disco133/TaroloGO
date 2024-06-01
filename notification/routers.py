from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

from user.models import UserProfile
from notification.models import NotificationStatus, NotificationType, SystemNotification, UserSystemNotification
from notification.schemas import (NotificationStatusCreate, NotificationTypeCreate, NotificationTypeOut, NotificationStatusOut,
NotificationByUserOut, SystemNotificationOut, SystemNotificationCreate)
from database import get_session
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(
    prefix='/notification',
    tags=['Notification']
)


# функция для создания статуса уведомления
async def create_notification_status(stat: NotificationStatusCreate, session: AsyncSession = Depends(get_session)):
    db_notification_status = NotificationStatus(
        notification_status_name=stat.notification_status_name
    )
    session.add(db_notification_status)
    await session.commit()
    await session.refresh(db_notification_status)
    return db_notification_status


# создание статуса уведомления
@router.post("/create_status", response_model=NotificationStatusOut)
async def create_notification_status_endpoint(stat: NotificationStatusCreate, session: AsyncSession = Depends(get_session)):
    db_status = await create_notification_status(stat, session)
    if db_status is None:
        raise HTTPException(status_code=400, detail="Notification status creation failed")
    return db_status


# название статуса уведомления по его айди
@router.get("/find/{notification_status_id}")
async def read_notification_status(notification_status_id: int, session: AsyncSession = Depends(get_session)):
    read_notification_status_query = await session.execute(select(NotificationStatus).filter(
        NotificationStatus.notification_status_id == notification_status_id))
    db_read_notification_status = read_notification_status_query.scalars().first()
    if not db_read_notification_status:
        raise HTTPException(status_code=404, detail='Notification Status is not found')
    return db_read_notification_status


# функция для удаления статуса уведомления
async def delete_notification_status(notification_status_id: int, session: AsyncSession = Depends(get_session)):
    delete_notification_status_query = await session.execute(select(NotificationStatus).filter(
        NotificationStatus.notification_status_id == notification_status_id))
    db_delete_notification_status = delete_notification_status_query.scalars().first()
    if not db_delete_notification_status:
        raise HTTPException(status_code=404, detail="Notification status not found")
    await session.delete(db_delete_notification_status)
    await session.commit()
    return {"message": "Notification status deleted successfully"}


# удаление статуса уведомления
@router.delete("/delete_notification_status/{notification_status_id}")
async def delete_notification_status_endpoint(notification_status_id: int, session: AsyncSession = Depends(get_session)):
    return await delete_notification_status(notification_status_id, session)


###############################
#      Notification_type      #
###############################


# функция для создания типа уведомления
async def create_notification_type(n_type: NotificationTypeCreate, session: AsyncSession = Depends(get_session)):
    db_type = NotificationType(
        notification_type_name=n_type.notification_type_name
    )
    session.add(db_type)
    await session.commit()
    await session.refresh(db_type)
    return db_type


# создание типа уведомления
@router.post("/create_type", response_model=NotificationTypeOut)
async def create_notification_type_endpoint(n_type: NotificationTypeCreate, session: AsyncSession = Depends(get_session)):
    db_create_type = await create_notification_type(n_type, session)
    if db_create_type is None:
        raise HTTPException(status_code=400, detail="Notification type creation failed")
    return db_create_type


# название типа уведомления по его айди
@router.get("/find_type/{notification_type_id}")
async def read_notification_status(notification_type_id: int, session: AsyncSession = Depends(get_session)):
    find_notification_type_query = await session.execute(select(NotificationType).filter(
        NotificationType.notification_type_id == notification_type_id))
    db_find_notification_type = find_notification_type_query.scalars().first()
    if not db_find_notification_type:
        raise HTTPException(status_code=404, detail='Notification type is not found')
    return db_find_notification_type


# функция для удаления типа уведомления
async def delete_notification_type(notification_type_id: int, session: AsyncSession = Depends(get_session)):
    delete_notification_type_query = await session.execute(select(NotificationType).filter(
        NotificationType.notification_type_id == notification_type_id))
    db_delete_notification_type = delete_notification_type_query.scalars().first()
    if not db_delete_notification_type:
        raise HTTPException(status_code=404, detail="Notification type not found")
    await session.delete(db_delete_notification_type)
    await session.commit()
    return {"message": "Notification type deleted successfully"}


# удаление типа уведомления
@router.delete("/delete_type/{notification_type_id}")
async def delete_notification_type_endpoint(notification_type_id: int, session: AsyncSession = Depends(get_session)):
    return await delete_notification_type(notification_type_id, session)


###############################
#     System_notification     #
###############################


# функция для создания уведомления
async def create_notification(notification: SystemNotificationCreate, session: AsyncSession = Depends(get_session)):
    db_notification = SystemNotification(
        notification_status_id=notification.notification_status_id,
        notification_type_id=notification.notification_type_id,
        notification_title=notification.notification_title,
        notification_text=notification.notification_text,
        notification_date_time=notification.notification_date_time
    )
    session.add(db_notification)
    await session.commit()
    await session.refresh(db_notification)
    return db_notification


# создание уведомления
@router.post("/create_notification", response_model=SystemNotificationOut)
async def create_notification_endpoint(notification: SystemNotificationCreate, session: AsyncSession = Depends(get_session)):
    db_notification = await create_notification(notification, session)
    if db_notification is None:
        raise HTTPException(status_code=400, detail="Notification creation failed")
    return db_notification


# название уведомления по его айди
@router.get("/find_notification/{notification_id}")
async def read_notification(notification_id: int, session: AsyncSession = Depends(get_session)):
    find_notification_query = await session.execute(select(SystemNotification).filter(
        SystemNotification.notification_id == notification_id))
    db_find_notification = find_notification_query.scalars().first()
    if not db_find_notification:
        raise HTTPException(status_code=404, detail='Notification is not found')
    return db_find_notification


# функция для удаления Уведомления
async def delete_notification(notification_id: int, session: AsyncSession = Depends(get_session)):
    delete_notification_query = await session.execute(select(SystemNotification).filter(
        SystemNotification.notification_id == notification_id))
    db_delete_notification = delete_notification_query.scalars().first()
    if not db_delete_notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    await session.delete(db_delete_notification)
    await session.commit()
    return {"message": "Notification deleted successfully"}


# удаление уведомления
@router.delete("/delete_notification/{notification_id}")
async def delete_notification_endpoint(notification_id: int, session: AsyncSession = Depends(get_session)):
    return await delete_notification(notification_id, session)


###############################
#      user_notification      #
###############################


# Function to create a notification bond for a list of users
async def create_user_notifications_bond(user_ids: List[int], notification_id: int, session: AsyncSession = Depends(get_session)):
    db_user_notifications = [
        UserSystemNotification(user_id=user_id, notification_id=notification_id)
        for user_id in user_ids
    ]
    session.add_all(db_user_notifications)
    await session.commit()
    return db_user_notifications


# Endpoint to create notification for all users or users with a specific role
@router.post("/create_notification_by_role/{role_id}", response_model=List[SystemNotificationOut])
async def create_user_notification(role_id: int, notification_id: int, session: AsyncSession = Depends(get_session)):
    if role_id == 0:
        # Get all users
        users_query = select(UserProfile)
    else:
        # Get users with the specific role
        users_query = select(UserProfile).filter(UserProfile.role_id == role_id)

    result = await session.execute(users_query)
    users = result.scalars().all()

    if not users:
        raise HTTPException(status_code=404, detail="No users found")

    user_ids = [user.user_id for user in users]
    db_user_notifications = await create_user_notifications_bond(user_ids, notification_id, session)

    if not db_user_notifications:
        raise HTTPException(status_code=400, detail="Failed to create notifications")

    return db_user_notifications


@router.get("/user/{user_id}", response_model=List[NotificationByUserOut])
async def get_user_notifications(user_id: int, session: AsyncSession = Depends(get_session)):
    user_notifications_query = select(
        SystemNotification.notification_title,
        SystemNotification.notification_text
    ).join(
        UserSystemNotification,
        UserSystemNotification.notification_id == SystemNotification.notification_id
    ).filter(
        UserSystemNotification.user_id == user_id
    )

    result = await session.execute(user_notifications_query)
    user_notifications = result.fetchall()

    if not user_notifications:
        raise HTTPException(status_code=404, detail="No notifications found for this user")

    return [
        NotificationByUserOut(notification_title=notif.notification_title, notification_text=notif.notification_text)
        for notif in user_notifications]
