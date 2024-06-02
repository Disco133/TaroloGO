from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, UniqueConstraint
from database import Base


class NotificationStatus(Base):
    __tablename__ = 'notification_status'
    notification_status_id = Column(Integer, primary_key=True, index=True)
    notification_status_name = Column(String, index=True)


class NotificationType(Base):
    __tablename__ = "notification_type"
    notification_type_id = Column(Integer, primary_key=True, index=True)
    notification_type_name = Column(String, index=True)


class SystemNotification(Base):
    __tablename__ = 'system_notification'
    notification_id = Column(Integer, primary_key=True, index=True)
    notification_status_id = Column(Integer, ForeignKey('notification_status.notification_status_id'))
    notification_type_id = Column(Integer, ForeignKey('notification_type.notification_type_id'))
    notification_title = Column(String, index=True)
    notification_text = Column(String, index=True)
    notification_date_time = Column(DateTime, nullable=False, default=func.now())


class UserSystemNotification(Base):
    __tablename__ = 'user_system_notification'
    user_notification_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user_profile.user_id'))
    notification_id = Column(Integer, ForeignKey('system_notification.notification_id'))
    __table_args__ = (
        UniqueConstraint('user_id', 'notification_id', name='_user_notification_uc'),
    )