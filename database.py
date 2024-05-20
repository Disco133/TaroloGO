from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://postgres:taro123123@localhost:5432/TaroloGO"  # ссылка на базу данных

engine = create_engine(DATABASE_URL)  # создание движка для подключения к базе данных

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)  # создание сессии базы данных

Base = declarative_base()  # для работы с базой данных не через sql-запросы, а с помощью python классов
