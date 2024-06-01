from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


from database import get_session
from favorite.models import UserFavoriteTarots
from favorite.schemas import UserFavoriteTarotsCreate, UserFavoriteTarotsOut

router = APIRouter(
    prefix='/user_favorite_tarots',
    tags=['Favorite']
)


# функция добавление таролога в избранные
async def create_user_favorite_tarot(favorite: UserFavoriteTarotsCreate, session: AsyncSession = Depends(get_session)):
   db_favorite = UserFavoriteTarots(
       user_id=favorite.user_id,
       tarot_id=favorite.tarot_id
   )
   session.add(db_favorite)
   await session.commit()
   await session.refresh(db_favorite)
   return db_favorite


# добавление таролога в избранные
@router.post("/create", response_model=UserFavoriteTarotsOut)
async def create_user_favorite_tarot_endpoint(favorite: UserFavoriteTarotsCreate, session: AsyncSession = Depends(get_session)):
   db_favorite = await create_user_favorite_tarot(favorite, session)
   if db_favorite is None:
       raise HTTPException(status_code=400, detail="Favorite creation failed")
   return db_favorite


# получение всех тарологов в избранных у пользователя
@router.get('/{user_id}', response_model=List[UserFavoriteTarotsOut])
async def read_user_favorite_tarots(user_id: int, session: AsyncSession = Depends(get_session)):
    read_favorite_query = (
        await session.execute(
            select(UserFavoriteTarots)
            .filter(UserFavoriteTarots.user_id == user_id)
        )
    )
    db_favorite = read_favorite_query.scalars().all()
    if not db_favorite:
       raise HTTPException(status_code=404, detail="No favorites found for this user")
    return db_favorite


# функция для удаления таролога из избранных
async def delete_user_favorite_tarot(user_id: int, tarot_id, session: AsyncSession = Depends(get_session)):
   delete_favorite_query = await session.execute(select(UserFavoriteTarots).filter(
       UserFavoriteTarots.user_id == user_id,
       UserFavoriteTarots.user_id == user_id))
   favorite_query = delete_favorite_query.scalars().first()
   if not favorite_query:
       raise HTTPException(status_code=404, detail="Favorite not found")
   await session.delete(favorite_query)
   await session.commit()
   return {"message": "Favorite tarot deleted successfully"}


# удаление таролога из избранных
@router.delete("/{user_id}/{tarot_id}")
async def delete_user_favorite_tarot_endpoint(user_id: int, tarot_id: int, session: AsyncSession = Depends(get_session)):
   return await delete_user_favorite_tarot(user_id, tarot_id, session)

