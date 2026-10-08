# Действия с БД

from src.database.models import ShortURL

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from src.exceptions import SlugAlreadyExistsError

async def add_slug_to_database(
    slug: str,
    long_url: str,
    session: AsyncSession,
):
    # Создаем объект
    new_slug = ShortURL(
        slug=slug,
        long_url=long_url,
    )
    # Добавляем его в session
    session.add(new_slug)
    try:
        # Фиксируем изменения в БД и закрываем транзакцию
        await session.commit()
    except IntegrityError:
        # это ошибка вставки, значит такой слаг уже существует, то нужно сгенерировать новый слаг и попробовать снова
        raise SlugAlreadyExistsError()
        

async def get_long_url_by_slug_from_database(
    slug: str,
    session: AsyncSession
) -> str | None:
    # Начинается транзакция. Делаем запрос:
    query = select(ShortURL).filter_by(slug=slug)
    result = await session.execute(query)
    res: ShortURL | None = result.scalar_one_or_none()
    return res.long_url if res.long_url else None
