from contextlib import asynccontextmanager
from fastapi import FastAPI, Body, status, HTTPException, Depends
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
load_dotenv()
from src.database.db import engine, new_session
from src.database.models import Base
from src.service import generate_short_url, get_url_by_slug
from src.exceptions import NoLongUrlFoundError, SlugAlreadyExistsError
from typing import AsyncGenerator, Annotated
from sqlalchemy.ext.asyncio import AsyncSession

# Жизненный цикл приложения. До запуска приложения подключаемся к БД и создаем модели
# Код выполнится ровно один раз при старте приложения до того, как сервер начнет принимать HTTP-запросы
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

# app.add_middleware(
#     CORSMiddleware, 
#     allow_origins=["http://localhost:3000"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# создаем конкретную сессию из фабрики new_session и потом ее передаем в Depends для обработчика запроса
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with new_session() as session:
        yield session

# Эндпоинт для генерации короткой ссылки, принимает длинную ссылку в теле запроса и возвращает короткую ссылку
# Depends это параметр для внедрения зависимостей
# FastAPI сам создает сессию и передает ее в обработчик запроса
@app.post("/short_url")
async def generate_slug(
    long_url: Annotated[str, Body(embed=True)],
    session: Annotated[AsyncSession, Depends(get_session)]
):
    try:
        new_slug = await generate_short_url(long_url, session)
        return {"data": new_slug}
    except SlugAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Не удалось сгенерировать slug"
        )

# Эндпоинт получения слага (с дальнейшим редиректом)
@app.get("/{slug}")
async def redirect_to_url(
    slug: str, 
    session: Annotated[AsyncSession, Depends(get_session)]
):
    # при переходе по короткой ссылке, нужно получить из базы данных длинную ссылку и сделать редирект на нее
    # то есть будет переходить по нашей ссылке, а попадет на свой сайт, который был передан в теле запроса при генерации короткой ссылки
    try:
        long_url = await get_url_by_slug(slug, session)
        return RedirectResponse(url=long_url, status_code=status.HTTP_302_FOUND)
    except NoLongUrlFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ссылка не найдена")