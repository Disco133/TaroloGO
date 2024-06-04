import uvicorn
from fastapi import FastAPI
# from fastapi_cache import FastAPICache
# from fastapi_cache.backends.redis import RedisBackend
# from redis import asyncio as aioredis


from database import engine, Base
from user.routers import router as users_router
from role.routers import router as role_router
from specialization.routers import router as specialization_router
from service.routers import router as service_router
from message.routers import router as message_router
from notification.routers import router as notification_router
from feedback.roters import router as feedback_router
from user_service_history.routers import router as history_router
from favorite.routers import router as favorite_router
from status.routers import router as status_router


app = FastAPI(
    title='TaroloGO'
)

# Функция для создания всех таблиц
async def create_all_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Добавление события при запуске
@app.on_event("startup")
async def on_startup():
    await create_all_tables()

app.include_router(users_router, tags=["User"])
app.include_router(role_router, tags=['Role'])
app.include_router(specialization_router, tags=['Specialization'])
app.include_router(service_router, tags=['Service'])
app.include_router(message_router, tags=['Message/Contacts'])
app.include_router(notification_router, tags=['Notification'])
app.include_router(feedback_router, tags=['Feedback'])
app.include_router(history_router, tags=['History'])
app.include_router(favorite_router, tags=['Favorite'])
app.include_router(status_router, tags=['Status'])


# @app.on_event("startup")
# async def startup_event():
#     redis = aioredis.from_url("redis://localhost", encoding="utf8", decode_responses=True)
#     FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")


# автоматический запуск uvicorn
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host='127.0.0.1',
        port=8000,
        reload=True
    )