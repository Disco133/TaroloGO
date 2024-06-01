from sqlalchemy import Column, Integer, String

from database import Base


class Status(Base):
   __tablename__ = 'status'

   status_id = Column(Integer, primary_key=True, index=True)
   status_name = Column(String, index=True, nullable=False, unique=True)

