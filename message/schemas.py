from datetime import datetime
from typing import List
from pydantic import BaseModel


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
    sender_id: int
    recipient_id: int
    message_text: str
    message_date_send: datetime


class MessagesResponses(BaseModel):
    sent_messages: List[MessageResponse]
    received_messages: List[MessageResponse]


class ContactsInfo(BaseModel):
    username: str
    message_text: str
    message_date_send: datetime


class ContactsResponse(BaseModel):
    messages: List[ContactsInfo]