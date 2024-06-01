from sqlalchemy import Column, Integer, ForeignKey, String

from database import Base


class Service(Base):
    __tablename__ = 'service'
    service_id = Column(Integer, primary_key=True, index=True)
    tarot_id = Column(Integer, ForeignKey('user_profile.user_id'))
    service_name = Column(String, index=True, nullable=False, unique=True)
    service_description = Column(String, nullable=True)
    specialization_id = Column(Integer, ForeignKey('specialization.specialization_id', ondelete='CASCADE'))
    service_price = Column(Integer, nullable=False)
