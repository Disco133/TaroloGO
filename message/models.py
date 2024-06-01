from sqlalchemy import Column, Integer, ForeignKey, DateTime, String, func, UniqueConstraint
from sqlalchemy.orm import relationship

from database import Base


class Message(Base):
    __tablename__ = 'message'
    message_id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey('user_profile.user_id'))
    recipient_id = Column(Integer, ForeignKey('user_profile.user_id'))
    message_text = Column(String, index=True)
    message_date_send = Column(DateTime, nullable=False, default=func.now())

    sender = relationship("UserProfile", foreign_keys=[sender_id])
    recipient = relationship("UserProfile", foreign_keys=[recipient_id])


class Contacts(Base):
    __tablename__ = 'contacts'
    contact_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user_profile.user_id'))
    user_contact_id = Column(Integer, ForeignKey('user_profile.user_id'))
    __table_args__ = (
        UniqueConstraint('user_id', 'user_contact_id', name='_user_contact_uc'),
    )