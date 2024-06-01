from sqlalchemy import  Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Specialization(Base):
    __tablename__ = 'specialization'

    specialization_id = Column(Integer, primary_key=True, index=True)
    specialization_name = Column(String, index=True, nullable=False, unique=True)


class TarotSpecialization(Base):
    __tablename__ = 'tarot_specialization'

    tarot_specialization_id = Column(Integer, primary_key=True, index=True)
    specialization_id = Column(Integer, ForeignKey('specialization.specialization_id'))
    tarot_id = Column(Integer, ForeignKey('user_profile.user_id'))
