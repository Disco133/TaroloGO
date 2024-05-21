from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Date, DateTime, Float, func
from sqlalchemy.orm import relationship
from database import Base


class Service(Base):
    __tablename__ = 'service'

    service_id = Column(Integer, primary_key=True, index=True)
    tarot_id = Column(Integer, ForeignKey('user_profile.user_id'))
    name_service = Column(String, index=True, nullable=False, unique=True)
    specialization_id = Column(Integer, ForeignKey('specialization.specialization_id'))
    service_price = Column(Integer, nullable=False)


class Specialization(Base):
    __tablename__ = 'specialization'

    specialization_id = Column(Integer, primary_key=True, index=True)
    specialization_name = Column(String, index=True, nullable=False, unique=True)


class Tarot_specialization(Base):
    __tablename__ = 'tarot_specialization'

    tarot_specialization_id = Column(Integer, primary_key=True, index=True)
    specialization_id = Column(Integer, ForeignKey('specialization.specialization_id'))
    user_id = Column(Integer, ForeignKey('user_profile.user_id'))


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
    # is_deleted = Column(Boolean, default=False)
    # profile_picture = Column(String, nullable=True)
    # tarot_description = Column(String, nullable=True)
    # tarot_experience = Column(Float, nullable=True)
    # tarot_rating = Column(Float, nullable=True)
