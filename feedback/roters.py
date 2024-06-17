from datetime import datetime, timedelta
from typing import List, Dict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, asc, delete

from user.models import UserProfile
from feedback.models import Feedback
from feedback.schemas import FeedbackRead, FeedbackCreate, FeedbackOut
from database import get_session
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix='/feedback',
    tags=['Feedback']
)


async def create_feedback(feedback: FeedbackCreate, session: AsyncSession = Depends(get_session)):
    # Проверяем, существует ли user_id в таблице user_profile
    create_feedback_query = await session.execute(select(UserProfile).filter(UserProfile.user_id == feedback.user_id))
    db_create_feedback = create_feedback_query.scalars().first()
    if not db_create_feedback:
        raise HTTPException(status_code=404, detail="User ID not found")

    # Преобразование datetime в безвременную зону
    feedback_datetime = feedback.feedback_datetime.replace(tzinfo=None)

    db_feedback = Feedback(
        user_id=feedback.user_id,
        feedback_text=feedback.feedback_text,
        feedback_datetime=feedback_datetime,
        is_read=False
    )
    session.add(db_feedback)
    await session.commit()
    await session.refresh(db_feedback)
    return db_feedback


# Создание отзыва
@router.post("/create", response_model=FeedbackOut)
async def create_feedback_endpoint(feedback: FeedbackCreate, session: AsyncSession = Depends(get_session)):
    db_feedback = await create_feedback(feedback, session)
    if db_feedback is None:
        raise HTTPException(status_code=400, detail="Feedback creation failed")
    return db_feedback


@router.post("/mark_oldest_unread_as_read", response_model=FeedbackRead)
async def mark_oldest_unread_as_read(session: AsyncSession = Depends(get_session)):
    feedback_read_query = await session.execute(select(Feedback).filter(Feedback.is_read == False).order_by(asc(Feedback.feedback_datetime)))
    db_feedback_read = feedback_read_query.scalars().first()
    if not db_feedback_read:
        raise HTTPException(status_code=404, detail="No unread feedback found")
    # Обновляем поле is_read на True
    db_feedback_read.is_read = True
    await session.commit()
    await session.refresh(db_feedback_read)
    return FeedbackRead(feedback_id=db_feedback_read.feedback_id, feedback_text = db_feedback_read.feedback_text, is_read=db_feedback_read.is_read)


# вывод фитбека по feedback_id
@router.get("/find_feedback/{feedback_id}")
async def read_feedback(feedback_id: int, session: AsyncSession = Depends(get_session)):
    db_feedback = await session.execute(select(Feedback).filter(Feedback.feedback_id == feedback_id))
    db_feedback = db_feedback.scalar()

    if not db_feedback:
        raise HTTPException(status_code=404, detail="Feedback is not found")

    return db_feedback


# весь feedback пользователя
@router.get('/{user_id}', response_model=Dict[str, FeedbackOut])
async def read_user_feedback(user_id: int, session: AsyncSession = Depends(get_session)):
    read_feedback_query = (
        await session.execute(
            select(Feedback)
            .filter(Feedback.user_id == user_id)
        )
    )
    db_feedback = read_feedback_query.scalars().all()
    if not db_feedback:
        raise HTTPException(status_code=404, detail="Feedbacks is not found")

    feedbacks = {}
    for index, feedback in enumerate(db_feedback, start=1):
        feedbacks[str(index)] = feedback

    return feedbacks


@router.delete("/delete_old_reads")
async def delete_old_read_feedbacks(session: AsyncSession = Depends(get_session)):
    fourteen_days_ago = datetime.now() - timedelta(days=14)
    # Удаляем записи
    delete_query = (
        delete(Feedback)
        .where(Feedback.is_read == True)
        .where(Feedback.feedback_datetime < fourteen_days_ago)
    )
    result = await session.execute(delete_query)
    await session.commit()
    return {"deleted_rows": result.rowcount}