# Бизнес-логика для создания slug и для получения URL по slug
# Абстракция от БД выполнена через передачу session через параметры

from sqlalchemy.ext.asyncio import AsyncSession
from src.shortener import generate_random_slug
from src.database.crud import add_slug_to_database, get_long_url_by_slug_from_database
from src.exceptions import NoLongUrlFoundError, SlugAlreadyExistsError

async def generate_short_url(
    long_url: str,
    session: AsyncSession
) -> str:
    async def _generate_slug_and_add_to_db() -> str:
        # 1 генерим слаг
        slug = generate_random_slug()
        # 2 добавляем в базу
        await add_slug_to_database(slug, long_url, session)
        return slug
    

    for attempt in range(5):
        try:
            slug = await _generate_slug_and_add_to_db()
            return slug
        except SlugAlreadyExistsError as ex:
            if attempt == 4:
                raise SlugAlreadyExistsError from ex

async def get_url_by_slug(slug: str, session: AsyncSession) -> str:
    long_url = await get_long_url_by_slug_from_database(slug, session)
    if not long_url:
        raise NoLongUrlFoundError()
    return long_url

