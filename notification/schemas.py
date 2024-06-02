from datetime import datetime

from pydantic import BaseModel


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


class UserSystemNotificationCreate(BaseModel):
    user_id: int
    notification_id: int


class UserSystemNotificationOut(BaseModel):
    user_id: int
    notification_id: int


class NotificationByUserOut(BaseModel):
    notification_title: str
    notification_text: str