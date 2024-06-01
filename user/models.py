from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Date, DateTime, Float, func, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base


class UserProfile(Base):
    __tablename__ = 'user_profile'

    user_id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey('role.role_id'))
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
