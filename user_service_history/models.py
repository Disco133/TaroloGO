from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func

from database import Base


class UserServiceHistory(Base):
    __tablename__ = 'user_service_history'
    history_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user_profile.user_id'))
    service_id = Column(Integer, ForeignKey('service.service_id'))
    tarot_id = Column(Integer, unique=False, nullable=False, index=True)
    status_id = Column(Integer, ForeignKey('status.status_id', ondelete='CASCADE'))
    review_title = Column(String, nullable=True)
    review_text = Column(String, nullable=True)
    review_value = Column(Integer, nullable=True, default=0)
    review_date_time = Column(DateTime, nullable=True, default=func.now())
