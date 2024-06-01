from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from user.models import UserProfile
from role.models import Role
from role.schemas import RoleCreate, RoleOut
from database import get_session
from sqlalchemy.ext.asyncio import AsyncSession



router = APIRouter(
    prefix='/role',
    tags=['Role']
)


# Функция для создания роли
async def create_role(role: RoleCreate, session: AsyncSession = Depends(get_session)):
    db_role = Role(
        role_name=role.role_name
    )
    session.add(db_role)
    await session.commit()
    await session.refresh(db_role)
    return db_role


# создание роли
@router.post("/crate", response_model=RoleOut)
async def create_role_endpoint(role: RoleCreate, session: AsyncSession = Depends(get_session)):
    db_role = await create_role(role, session)
    if db_role is None:
        raise HTTPException(status_code=400, detail="Role creation failed")
    return db_role


# название роли по её айди
@router.get("/{role_id}")
async def read_user(role_id: int, session: AsyncSession = Depends(get_session)):
    role_query = await session.execute(select(Role).filter(Role.role_id == role_id))
    db_role = role_query.scalars().first()
    if not db_role:
        raise HTTPException(status_code=404, detail='Role is not found')
    return db_role


# выводит всех юзеров по определённой роли
@router.get('/users/{role_id}')
async def read_users_by_role(role_id: int, session: AsyncSession = Depends(get_session)):
    read_role_query = await session.execute(select(UserProfile).join(Role).filter(UserProfile.role_id == role_id))
    db_read_role = read_role_query.scalars().all()
    if not db_read_role:
        raise HTTPException(status_code=404, detail='Role is not found')
    users = [{'users_name': users.username} for users in db_read_role]
    return {'role_id': role_id, 'username': users}


# функция для удаления роли
async def delete_role(role_id: int, session: AsyncSession = Depends(get_session)):
    delete_role_query = await session.execute(select(Role).filter(Role.role_id == role_id))
    db_role_delete = delete_role_query.scalars().first()
    if not db_role_delete:
        raise HTTPException(status_code=404, detail="Role not found")
    await session.delete(db_role_delete)
    await session.commit()
    return {"message": "Role deleted successfully"}


# удаление роли
@router.delete("/delete/{role_id}")
async def delete_user_endpoint(role_id: int, session: AsyncSession = Depends(get_session)):
    return await delete_role(role_id, session)


