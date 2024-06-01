from datetime import datetime
from typing import List

import bcrypt
from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from favorite.models import UserFavoriteTarots
from favorite.schemas import UserFavoriteTarotsOut
from user.models import UserProfile
from user.schemas import UserCreate, UserOut
from database import get_session
from favorite.routers import read_user_favorite_tarots
from message.routers import get_last_message

router = APIRouter(
    prefix='/user',
    tags=['User']
)


async def hash_password(password: str) -> str:
    # Генерируем соль
    salt = bcrypt.gensalt()
    # Хешируем пароль с использованием соли
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')


# функция сверки пароля с его хеш версией
async def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


# Функция для создания пользователя
async def create_user(user: UserCreate, session: AsyncSession = Depends(get_session)):
    hashed_password = await hash_password(user.password)
    db_user = UserProfile(
        username=user.username,
        role_id=user.role_id,
        email=user.email,
        phone_number=user.phone_number,
        password_hashed=hashed_password,
        date_birth=user.date_birth
    )
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


# создание юзера
@router.post("/create", response_model=UserOut)
async def create_user_endpoint(user: UserCreate, session: AsyncSession = Depends(get_session)):
    db_user = await create_user(user, session)
    if db_user is None:
        raise HTTPException(status_code=400, detail="User creation failed")
    return db_user


# обновление статуса is_delete
@router.post("/update_is_deleted/{user_id}")
async def update_user_is_deleted(user_id: int, is_deleted: bool, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(UserProfile).filter(UserProfile.user_id == user_id))
    db_user = result.scalars().first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db_user.is_deleted = is_deleted
    await session.commit()
    await session.refresh(db_user)
    return {"message": "User is_deleted updated successfully"}


# обновление имени в профиле
@router.post("/update_first_name/{user_id}")
async def update_user_first_name(user_id: int, first_name: str, session: AsyncSession = Depends(get_session)):
    db_user = await session.execute(select(UserProfile).filter(UserProfile.user_id == user_id))
    db_user = db_user.scalar()  # получаем результат из запроса

    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db_user.first_name = first_name
    await session.commit()
    await session.refresh(db_user)

    return {"message": "User first_name updated successfully"}

# обновление фамилии в профиле
@router.post("/update_second_name/{user_id}")
async def update_user_second_name(user_id: int, second_name: str, session: AsyncSession = Depends(get_session)):
    db_user = await session.execute(select(UserProfile).filter(UserProfile.user_id == user_id))
    db_user = db_user.scalar()

    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db_user.second_name = second_name
    await session.commit()
    await session.refresh(db_user)
    return {"message": "User second_name updated successfully"}


# обновление даты рождения в профиле
@router.post("/update_date_birth/{user_id}")
async def update_date_birth(user_id: int, date_birth: datetime, session: AsyncSession = Depends(get_session)):
    db_user = await session.execute(select(UserProfile).filter(UserProfile.user_id == user_id))
    db_user = db_user.scalar()

    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db_user.date_birth = date_birth
    await session.commit()
    await session.refresh(db_user)
    return {"message": "User date_birth updated successfully"}


# обновление описания таролога
@router.post("/update_description/{user_id}")
async def update_user_description(user_id: int, user_description: str, session: AsyncSession = Depends(get_session)):
    db_user = await session.execute(select(UserProfile).filter(UserProfile.user_id == user_id))
    db_user = db_user.scalar()

    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db_user.user_description = user_description
    await session.commit()
    await session.refresh(db_user)
    return {"message": "User description updated successfully"}


# обновление опыта работы таролога
@router.post("/update_tarot_experience/{user_id}")
async def update_tarot_experience(user_id: int, tarot_experience: float, session: AsyncSession = Depends(get_session)):
    db_user = await session.execute(select(UserProfile).filter(UserProfile.user_id == user_id))
    db_user = db_user.scalar()

    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if db_user.role_id != 1:  # Предполагается, что role_id для таролога равен 1
        raise HTTPException(status_code=403, detail="User does not have the required role")

    db_user.tarot_experience = tarot_experience
    await session.commit()
    await session.refresh(db_user)
    return {"message": "User tarot_experience updated successfully"}


# юзер по айди
@router.get("/find/{user_id}")
async def read_user(user_id: int, session: AsyncSession = Depends(get_session)):
    db_user = await session.execute(select(UserProfile).filter(UserProfile.user_id == user_id))
    db_user = db_user.scalar()

    if not db_user:
        raise HTTPException(status_code=404, detail="User is not found")

    return db_user



async def authenticate_user(email: str, password: str, session: AsyncSession = Depends(get_session)):
    # Получаем данные пользователя по email
    user = await session.execute(select(UserProfile).filter(UserProfile.email == email))
    db_user = user.scalars().first()
    if not db_user:
        raise HTTPException(status_code=401, detail='Неправильные email или пароль')

    # Проверяем введенный пароль с хешированным паролем из базы данных
    if not await verify_password(password, db_user.password_hashed):
        raise HTTPException(status_code=401, detail='Неправильные email или пароль')

    return db_user


# вывод всех тарологов
@router.get('/find_tarot')
async def read_tarot(session: AsyncSession = Depends(get_session)):
    read_tarot_query = await session.execute(select(UserProfile).filter(UserProfile.role_id == 1))
    db_users = read_tarot_query.scalars().all()
    if not db_users:
        raise HTTPException(status_code=404, detail='Tarot is not found')

    tarots = []
    for user in db_users:
        tarot_info = {
            'tarot_id': user.user_id,
            'first_name': user.first_name,
            'second_name': user.second_name,
            'tarot_description': user.user_description,
            'tarot_rating': user.tarot_rating,
            'reviews_count': 0  # по умолчанию количество отзывов 0
        }
        tarots.append(tarot_info)

    return tarots


@router.get('/get_info')
async def get_info(email: str, password_hashed: str, session: AsyncSession = Depends(get_session)):
    # Проверяем аутентификацию пользователя
    user = await authenticate_user(email, password_hashed, session=session)

    # Получаем информацию о пользователе
    favorite_info = await read_user_favorite_tarots(user.user_id, session=session)

    # Получаем информацию о таро
    tarot_info = await read_tarot(session=session)

    # Получаем диалоги
    message_info = await get_last_message(user.user_id, session=session)

    return {"favorite_info": favorite_info, "tarot_info": tarot_info, "message_info": message_info}


# функция для удаления юзера
async def delete_user(user_id: int, session: AsyncSession = Depends(get_session)):
    db_user = await session.execute(select(UserProfile).filter(UserProfile.user_id == user_id))
    db_user = db_user.scalar()

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    await session.delete(db_user)
    await session.commit()

    return {"message": "User deleted successfully"}


# удаление юзера
@router.delete("/delete/{user_id}")
async def delete_user_endpoint(user_id: int, session: AsyncSession = Depends(get_session)):
    return await delete_user(user_id, session)



