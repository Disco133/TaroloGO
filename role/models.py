from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class Role(Base):
    __tablename__ = 'role'

    role_id = Column(Integer, primary_key=True, index=True)  # index = True для оптимизации
    role_name = Column(String, index=True, nullable=False, unique=True)



