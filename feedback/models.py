from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, Boolean

from database import Base


class Feedback(Base):
    __tablename__ = 'feedback'

    feedback_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user_profile.user_id'))
    feedback_text = Column(String, index=True)
    feedback_datetime = Column(DateTime, nullable=False, default=func.now())
    is_read = Column(Boolean)