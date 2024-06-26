from datetime import datetime
from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update, func
from sqlalchemy.orm import aliased
from user.models import UserProfile
from status.models import Status
from service.models import Service
from user_service_history.models import UserServiceHistory
from database import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from user_service_history.schemas import UserServiceHistoryCreate, UserServiceHistoryOut, UserServiceHistoryUpdateReview

router = APIRouter(
    prefix='/history',
    tags=['History']
)


# функция создание истории
async def create_history(history: UserServiceHistoryCreate, session: AsyncSession = Depends(get_session)):
    # Поиск службы по service_id
    create_history_query = await session.execute(select(Service).filter(Service.service_id == history.service_id))
    db_create_history = create_history_query.scalars().first()
    if not db_create_history:
        raise HTTPException(status_code=404, detail="Service not found")
    db_history = UserServiceHistory(
        user_id=history.user_id,
        service_id=history.service_id,
        tarot_id=db_create_history.tarot_id,
        status_id=history.status_id
    )
    session.add(db_history)
    await session.commit()
    await session.refresh(db_history)
    return db_history


# создание истории
@router.post("/create")
async def create_user_endpoint(history: UserServiceHistoryCreate, session: AsyncSession = Depends(get_session)):
    db_history_create = await create_history(history, session)
    if db_history_create is None:
        raise HTTPException(status_code=400, detail="History creation failed")
    return db_history_create


# Функция для обновления отзыва
async def update_review(history_update: UserServiceHistoryUpdateReview, session: AsyncSession = Depends(get_session)):
    history_review_update_query = await session.execute(select(UserServiceHistory).filter(
        UserServiceHistory.history_id == history_update.history_id))
    history_review_update = history_review_update_query.scalars().first()

    if not history_review_update:
        raise HTTPException(status_code=404, detail="History record not found")

    old_review_value = history_review_update.review_value
    history_review_update.review_title = history_update.review_title
    history_review_update.review_text = history_update.review_text
    history_review_update.review_date_time = datetime.utcnow()

    tarot_id = history_review_update.tarot_id
    await update_tarot_rating(tarot_id, old_review_value, history_update.review_value, session)
    history_review_update.review_value = history_update.review_value

    await session.commit()
    await session.refresh(history_review_update)
    return history_review_update


# Функция для обновления рейтинга таролога при добавлении новой оценки
async def update_tarot_rating(tarot_id: int, old_review_value: int, new_review_value: int, session: AsyncSession):
    tarot_rating_update_query = await session.execute(select(UserProfile).filter(UserProfile.user_id == tarot_id))
    db_tarot_rating_update = tarot_rating_update_query.scalars().first()
    if not db_tarot_rating_update:
        raise HTTPException(status_code=404, detail="Tarot profile not found")

    # Получаем текущие значения средней оценки и количество отзывов с review_value != 0
    current_reviews_query = await session.execute(select(UserServiceHistory).filter(
        UserServiceHistory.tarot_id == tarot_id,
        UserServiceHistory.review_value != 0
    ))
    current_reviews = current_reviews_query.scalars().all()
    current_reviews_count = len(current_reviews)
    print(current_reviews_count)
    if current_reviews_count == 0:
        db_tarot_rating_update.tarot_rating = new_review_value if new_review_value != 0 else None
    else:
        # Пересчитываем сумму всех отзывов с review_value != 0
        current_reviews_sum = sum(review.review_value for review in current_reviews)
        # Обновляем сумму с учетом нового и старого значения review_value
        new_reviews_sum = current_reviews_sum - old_review_value + new_review_value
        # Пересчитываем среднюю оценку
        new_rating = new_reviews_sum / (current_reviews_count + 1)
        # Обновляем среднюю оценку таролога в таблице UserProfile
        db_tarot_rating_update.tarot_rating = new_rating
        db_tarot_rating_update.review_count += 1
    await session.commit()


# Маршрут для обновления отзыва
@router.post("/update_review/{history_id}")
async def update_review_endpoint(history_update: UserServiceHistoryUpdateReview,
                                 session: AsyncSession = Depends(get_session)):
    updated_history = await update_review(history_update, session)
    return updated_history


# обновление статуса услуги
@router.post("/update_status/{history_id}")
async def update_service_status(history_id: int, status_id: int, session: AsyncSession = Depends(get_session)):
    update_service_status_query = await session.execute(
        select(UserServiceHistory).filter(UserServiceHistory.history_id == history_id))
    db_update_service_status = update_service_status_query.scalars().first()
    if db_update_service_status is None:
        raise HTTPException(status_code=404, detail="History record not found")
    service_status_query = await session.execute(select(Status).filter(
        Status.status_id == status_id))
    db_service_status = service_status_query.scalars().first()
    if db_service_status is None:
        raise HTTPException(status_code=404, detail="Status not found")
    db_update_service_status.status_id = status_id
    await session.commit()
    await session.refresh(db_service_status)
    return {"message": "Status updated successfully"}


# вывод user_service_history
@router.get("/{history_id}")
async def read_user_service_history(history_id: int, session: AsyncSession = Depends(get_session)):
    history_query = await session.execute(select(UserServiceHistory).filter(
        UserServiceHistory.history_id == history_id))
    history = history_query.scalars().first()
    if not history:
        raise HTTPException(status_code=404, detail='History is not found')
    return history


# все купленные услуги пользователя
@router.get('/{user_id}', response_model=Dict[str, UserServiceHistoryOut])
async def read_user_service_history(user_id: int, session: AsyncSession = Depends(get_session)):
    read_service_history_query = (
        await session.execute(
            select(UserServiceHistory.history_id,
                   UserServiceHistory.tarot_id,
                   UserServiceHistory.user_id,
                   UserServiceHistory.service_id,
                   UserServiceHistory.status_id,
                   UserProfile.first_name,
                   UserProfile.second_name,
                   Service.service_name,
                   Service.service_price
                   )
            .join(UserProfile, UserServiceHistory.tarot_id == UserProfile.user_id)
            .join(Service, UserServiceHistory.service_id == Service.service_id)
            .filter(UserServiceHistory.user_id == user_id)
        )
    )
    db_service_history = read_service_history_query.all()
    if not db_service_history:
        raise HTTPException(status_code=404, detail="No service history found for this tarot")

    service_history = {}
    for index, service in enumerate(db_service_history, start=1):
        history = UserServiceHistoryOut(
            history_id=service.history_id,
            tarot_id=service.tarot_id,
            user_id=service.user_id,
            service_id=service.service_id,
            status_id=service.status_id,
            first_name=service.first_name,
            second_name=service.second_name,
            service_name=service.service_name,
            service_price=service.service_price
        )
        service_history[str(index)] = history

    return service_history
