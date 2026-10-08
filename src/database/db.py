# Настройка движка для создания сессии БД

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
import os

DB_URL = os.getenv("DB_URL")

# Создаем асинхронный движок. Он отвечает за физическое подключение к БД.
engine = create_async_engine(
    url=DB_URL,
    pool_size=20, # количестве соединений
    max_overflow=30 # макс порого превышения количества соединений (те максимум будет 50)
)

# Фабрика (класс) для создания сессий
new_session = async_sessionmaker(bind=engine, expire_on_commit=False)

