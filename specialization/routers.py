from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from specialization.schemas import SpecCreate, SpecOut, TarotSpecializationOut, TarotSpecializationCreate
from specialization.models import Specialization, TarotSpecialization
from user.models import UserProfile
from database import get_session
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(
    prefix='/specialization',
    tags=['Specialization']
)


# Функция для создания специализации
async def create_specialization(spec: SpecCreate, session: AsyncSession = Depends(get_session)):
    db_spec = Specialization(
        specialization_name=spec.specialization_name
    )
    session.add(db_spec)
    await session.commit()
    await session.refresh(db_spec)
    return db_spec


# создания специализации
@router.post("/create", response_model=SpecOut)
async def create_specialization_endpoint(spec: SpecCreate, session: AsyncSession = Depends(get_session)):
    db_spec = await create_specialization(spec, session)
    if db_spec is None:
        raise HTTPException(status_code=400, detail="Specialization creation failed")
    return db_spec


# название специализации по её айди
@router.get("/find/{specialization_id}")
async def read_specialization(specialization_id: int, session: AsyncSession = Depends(get_session)):
    specialization_query = await session.execute(select(Specialization).filter(
        Specialization.specialization_id == specialization_id))
    db_create_specialization = specialization_query.scalars().first()
    if not db_create_specialization:
        raise HTTPException(status_code=404, detail='Specialization is not found')
    return db_create_specialization


# функция для удаления специализации
async def delete_specialization(specialization_id: int, session: AsyncSession = Depends(get_session)):
    delete_specialization_query = await session.execute(select(Specialization).filter(
        Specialization.specialization_id == specialization_id))
    db_delete_specialization = delete_specialization_query.scalar()
    if not db_delete_specialization:
        raise HTTPException(status_code=404, detail="Specialization not found")
    await session.delete(db_delete_specialization)
    await session.commit()
    return {"message": "Specialization deleted successfully"}


# удаление специализации
@router.delete("/delete/{specialization_id}")
async def delete_specialization_endpoint(specialization_id: int, session: AsyncSession = Depends(get_session)):
    return await delete_specialization(specialization_id, session)


###########################################################################################################


# Функция для создания связи таролог - специализация
async def create_specialization_bond(spec_bond: TarotSpecializationCreate, session: AsyncSession = Depends(get_session)):
    specialization_bond_query = await session.execute(select(UserProfile).filter(UserProfile.user_id == spec_bond.tarot_id))
    db_specialization_bond = specialization_bond_query.scalar()
    if db_specialization_bond is None:
        raise HTTPException(status_code=404, detail="User not found")
    if db_specialization_bond.role_id != 1:  # Предполагается, что role_id для таролога равен 1
        raise HTTPException(status_code=403, detail="User does not have the required role")
    db_spec_bond = TarotSpecialization(
        specialization_id=spec_bond.specialization_id,
        tarot_id=spec_bond.tarot_id
    )
    session.add(db_spec_bond)
    await session.commit()
    await session.refresh(db_spec_bond)
    return db_spec_bond


# таблица связи юзер-специализация
@router.post("/create_bond", response_model=TarotSpecializationOut)
async def create_specialization_endpoint(spec_bond: TarotSpecializationCreate, session: AsyncSession = Depends(get_session)):
    db_spec_bond = await create_specialization_bond(spec_bond, session)
    if db_spec_bond is None:
        raise HTTPException(status_code=400, detail="Specialization bond creation failed")
    return db_spec_bond


# выводит все специализации определённого таролога
@router.get("/tarot_specializations/{tarot_id}")
async def read_specialization_by_tarot(tarot_id: int, session: AsyncSession = Depends(get_session)):
    read_specialization_bond_query = (
        await session.execute(
            select(Specialization.specialization_name)
            .join(TarotSpecialization, TarotSpecialization.specialization_id == Specialization.specialization_id)
            .join(UserProfile, UserProfile.user_id == TarotSpecialization.tarot_id)
            .filter(UserProfile.user_id == tarot_id)
        )
    )

    db_read_specialization_bond = read_specialization_bond_query.scalars().all()

    if not db_read_specialization_bond:
        raise HTTPException(status_code=404, detail="Tarot is not found")

    specializations = [
        {"specialization_name": specialization}
        for specialization in db_read_specialization_bond
    ]

    return {"tarot_id": tarot_id, "specializations": specializations}


# выводит всех тарологов по определённой специализации
@router.get("/specialization_tarots/{specialization_id}")
async def read_tarot_by_specialization(specialization_id: int, session: AsyncSession = Depends(get_session)):
    specialization_bond_query = await session.execute(select(UserProfile).join(TarotSpecialization).join(Specialization)
        .filter(TarotSpecialization.specialization_id == specialization_id))
    db_specialization_bond = specialization_bond_query.scalars().all()
    if not db_specialization_bond:
        raise HTTPException(status_code=404, detail='Specialization is not found')
    tarots = [{'tarots_name': tarots.username} for tarots in db_specialization_bond]
    return {"specialization_id": specialization_id, "usernames": tarots}


# функция удаления связи таролог-специализация
async def delete_tarots_specialization(tarot_id: int, specialization_id: int, session: AsyncSession = Depends(get_session)):
    delete_tarot_specialization_query = await session.execute(select(TarotSpecialization).filter(
        TarotSpecialization.tarot_id == tarot_id,
        TarotSpecialization.specialization_id == specialization_id))
    db_delete_tarot_specialization = delete_tarot_specialization_query.scalar()
    if not db_delete_tarot_specialization:
        raise HTTPException(status_code=404, detail="Tarot/Specialization not found")
    await session.delete(db_delete_tarot_specialization)
    await session.commit()
    return {"message": "Tarot's specialization deleted successfully"}


# удаление связи таролог-специализация
@router.delete("/tarots/{tarot_id}/specialization/{specialization_id}")
async def delete_tarot_specialization_endpoint(tarot_id: int, specialization_id: int, session: AsyncSession = Depends(get_session)):
    return await delete_tarots_specialization(tarot_id, specialization_id, session)


