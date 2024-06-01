from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint

from database import Base


class UserFavoriteTarots(Base):
   __tablename__ = 'user_favorite_tarots'

   favorite_tarot_id = Column(Integer, primary_key=True, index=True)
   user_id = Column(Integer, ForeignKey('user_profile.user_id'))
   tarot_id = Column(Integer, ForeignKey('user_profile.user_id'))

   __table_args__ = (
       UniqueConstraint('user_id', 'tarot_id', name='user_favorite_tarots_uc'),
   )