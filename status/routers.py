from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from status.models import Status
from status.schemas import StatusCreate, StatusOut
from database import get_session

router = APIRouter(
    prefix='/status',
    tags=['Status']
)

# функция для создания статуса
async def create_status(stat: StatusCreate, session: AsyncSession = Depends(get_session)):
   db_stat = Status(
       status_name=stat.status_name
   )
   session.add(db_stat)
   await session.commit()
   await session.refresh(db_stat)
   return db_stat


# создание статуса
@router.post("/create", response_model=StatusOut)
async def create_status_endpoint(stat: StatusCreate, session: AsyncSession = Depends(get_session)):
   db_status = await create_status(stat, session)
   if db_status is None:
       raise HTTPException(status_code=400, detail="Status creation failed")
   return db_status


# название статуса по его айди
@router.get("/{status_id}")
async def read_status(status_id: int, session: AsyncSession = Depends(get_session)):
   status_query = await session.execute(select(Status).filter(Status.status_id == status_id))
   db_status = status_query.scalars().first()
   if not db_status:
       raise HTTPException(status_code=404, detail='Status is not found')
   return db_status


# функция для удаления статуса
async def delete_status(status_id: int, session: AsyncSession = Depends(get_session)):
   status_query = await session.execute(select(Status).filter(Status.status_id == status_id))
   db_status = status_query.scalars().first()
   if not db_status:
       raise HTTPException(status_code=404, detail="Status not found")
   await session.delete(db_status)
   await session.commit()
   return {"message": "Status deleted successfully"}


# удаление статуса
@router.delete("/delete/{status_id}")
async def delete_status_endpoint(status_id: int, session: AsyncSession = Depends(get_session)):
   return await delete_status(status_id, session)

