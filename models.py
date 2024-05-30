from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Date, DateTime, Float, func, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base


class UserFavoriteTarots(Base):
    __tablename__ = 'user_favorite_tarots'

    favorite_tarot_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user_profile.user_id'))
    tarot_id = Column(Integer, ForeignKey('user_profile.user_id'))

    __table_args__ = (
        UniqueConstraint('user_id', 'tarot_id', name='user_favorite_tarots_uc'),
    )


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


class Service(Base):
    __tablename__ = 'service'

    service_id = Column(Integer, primary_key=True, index=True)
    tarot_id = Column(Integer, ForeignKey('user_profile.user_id'))
    service_name = Column(String, index=True, nullable=False, unique=True)
    service_description = Column(String, nullable=True)
    specialization_id = Column(Integer, ForeignKey('specialization.specialization_id', ondelete='CASCADE'))
    service_price = Column(Integer, nullable=False)


class Specialization(Base):
    __tablename__ = 'specialization'

    specialization_id = Column(Integer, primary_key=True, index=True)
    specialization_name = Column(String, index=True, nullable=False, unique=True)


class Message(Base):
    __tablename__ = 'message'

    message_id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey('user_profile.user_id'))
    recipient_id = Column(Integer, ForeignKey('user_profile.user_id'))
    message_text = Column(String, index=True)
    message_date_send = Column(DateTime, nullable=False, default=func.now())
    message_date_read = Column(DateTime)

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


class TarotSpecialization(Base):
    __tablename__ = 'tarot_specialization'

    tarot_specialization_id = Column(Integer, primary_key=True, index=True)
    specialization_id = Column(Integer, ForeignKey('specialization.specialization_id'))
    tarot_id = Column(Integer, ForeignKey('user_profile.user_id'))


class Role(Base):
    __tablename__ = 'role'

    role_id = Column(Integer, primary_key=True, index=True)  # index = True для оптимизации
    role_name = Column(String, index=True, nullable=False, unique=True)


class UserProfile(Base):
    __tablename__ = 'user_profile'

    user_id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey('role.role_id', ondelete='CASCADE'))
    username = Column(String, index=True, nullable=False, unique=True)
    email = Column(String, index=True, unique=True, nullable=False)
    phone_number = Column(String, unique=True, nullable=False, index=True)
    password_hashed = Column(String, nullable=False)
    first_name = Column(String, nullable=True)
    second_name = Column(String, nullable=True)
    date_birth = Column(Date, nullable=False)
    # last_seen = Column(DateTime, nullable=False)
    date_registration = Column(DateTime, nullable=False, default=func.now())
    is_deleted = Column(Boolean, default=False, nullable=False)
    # profile_picture = Column(String, nullable=True)
    user_description = Column(String, nullable=True)
    tarot_experience = Column(Float, nullable=True)
    tarot_rating = Column(Float, nullable=True, default=0)


class Status(Base):
    __tablename__ = 'status'

    status_id = Column(Integer, primary_key=True, index=True)
    status_name = Column(String, index=True, nullable=False, unique=True)


class UserServiceHistory(Base):
    __tablename__ = 'user_service_history'

    history_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user_profile.user_id', ondelete='CASCADE'))
    service_id = Column(Integer, ForeignKey('service.service_id', ondelete='CASCADE'))
    tarot_id = Column(Integer, unique=False, nullable=False, index=True)
    status_id = Column(Integer, ForeignKey('status.status_id', ondelete='CASCADE'))
    review_title = Column(String, nullable=True)
    review_text = Column(String, nullable=True)
    review_value = Column(Integer, nullable=True, default=0)
    review_date_time = Column(DateTime, nullable=True, default=func.now())


class UserSystemNotification(Base):
    __tablename__ = 'user_system_notification'

    user_notification_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user_profile.user_id'))
    notification_id = Column(Integer, ForeignKey('system_notification.notification_id'))

    __table_args__ = (
        UniqueConstraint('user_id', 'notification_id', name='_user_notification_uc'),
    )

