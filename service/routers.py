from typing import List, Dict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from service.schemas import ServiceCreate, ServiceOut
from service.models import Service
from user.models import UserProfile
from database import get_session
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(
    prefix='/service',
    tags=['Service']
)


# функция создания услуги
async def create_service(service: ServiceCreate, session: AsyncSession = Depends(get_session)):
    # Проверка, что пользователь с указанным tarot_id имеет роль таролога
    create_service_query = await session.execute(select(UserProfile).filter(UserProfile.user_id == service.tarot_id))
    db_create_service = create_service_query.scalars().first()
    if db_create_service is None:
        raise HTTPException(status_code=404, detail="User not found")
    if db_create_service.role_id != 1:  # Предполагается, что role_id для таролога равен 1
        raise HTTPException(status_code=403, detail="User does not have the required role")
    db_service = Service(
        service_name=service.service_name,
        tarot_id=service.tarot_id,
        specialization_id=service.specialization_id,
        service_price=service.service_price
    )
    session.add(db_service)
    await session.commit()
    await session.refresh(db_service)
    return db_service


# создание услуги
@router.post('/create', response_model=ServiceOut)
async def create_service_endpoint(service: ServiceCreate, session: AsyncSession = Depends(get_session)):
    db_service = await create_service(service, session)
    if db_service is None:
        raise HTTPException(status_code=400, detail="Service creation failed")
    return db_service


# обновление названия услуги
@router.post("/update_service_name/{service_id}")
async def update_service_name(service_id: int, service_name: str, session: AsyncSession = Depends(get_session)):
    service_name_query = await session.execute(select(Service).filter(Service.service_id == service_id))
    db_service_name = service_name_query.scalars().first()
    if db_service_name is None:
        raise HTTPException(status_code=404, detail="Service not found")
    db_service_name.service_name = service_name
    await session.commit()
    await session.refresh(db_service_name)
    return {"message": "Service name updated successfully"}


# обновление цены услуги
@router.post("/update_service_price/{service_id}")
async def update_service_price(service_id: int, service_price: int, session: AsyncSession = Depends(get_session)):
    service_price_query = await session.execute(select(Service).filter(Service.service_id == service_id))
    db_service_price = service_price_query.scalars().first()
    if db_service_price is None:
        raise HTTPException(status_code=404, detail="Service not found")
    db_service_price.service_price = service_price
    await session.commit()
    await session.refresh(db_service_price)
    return {"message": "Service price updated successfully"}


# обновление описания услуги
@router.post("/update_service_description/{service_id}")
async def update_service_description(service_id: int, service_description: str, session: AsyncSession = Depends(get_session)):
    service_description_query = await session.execute(select(Service).filter(Service.service_id == service_id))
    db_service_description = service_description_query.scalars().first()
    if db_service_description is None:
        raise HTTPException(status_code=404, detail="Service not found")
    db_service_description.service_description = service_description
    await session.commit()
    await session.refresh(db_service_description)
    return {"message": "Service description updated successfully"}


# услуга по айди
@router.get("/find/{service_id}")
async def read_service(service_id: int, session: AsyncSession = Depends(get_session)):
    find_service_query = await session.execute(select(Service).filter(Service.service_id == service_id))
    db_find_service = find_service_query.scalars().first()
    if not db_find_service:
        raise HTTPException(status_code=404, detail='Service is not found')
    return db_find_service


@router.get('/{tarot_id}', response_model=Dict[str, ServiceOut])
async def read_user_service(tarot_id: int, session: AsyncSession = Depends(get_session)):
    read_service_query = (
        await session.execute(
            select(Service)
            .filter(Service.tarot_id == tarot_id)
        )
    )
    db_service = read_service_query.scalars().all()
    if not db_service:
        raise HTTPException(status_code=404, detail="No services found for this tarot")

    services = {}
    for index, service in enumerate(db_service, start=1):
        services[str(index)] = service

    return services


# функция удаления услуги
async def delete_service(service_id: int, session: AsyncSession = Depends(get_session)):
    delete_service_query = await session.execute(select(Service).filter(
        Service.service_id == service_id))
    db_delete_service = delete_service_query.scalars().first()
    if not db_delete_service:
        raise HTTPException(status_code=404, detail="Service not found")
    await session.delete(db_delete_service)
    await session.commit()
    return {"message": "Service deleted successfully"}


# удаление услуги
@router.delete("/service/{service_id}")
async def delete_service_endpoint(service_id: int, session: AsyncSession = Depends(get_session)):
    return await delete_service(service_id, session)