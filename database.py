from typing import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+asyncpg://postgres:taro123123@localhost:5432/TaroloGO"  # ссылка на базу данных
Base = declarative_base()  # для работы с базой данных не через sql-запросы, а с помощью python классов

engine = create_async_engine(DATABASE_URL, echo=True)

# Создание фабрики асинхронных сессий
async_session_maker = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


async def get_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session
