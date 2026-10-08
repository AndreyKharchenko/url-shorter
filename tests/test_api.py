from httpx import AsyncClient

# тест для эндпоинта /short_url
async def test_generate_slug(ac: AsyncClient):
    result = await ac.post("/short_url", json={"long_url": "https://my-site.com"})
    assert result.status_code == 200

# тест для эндпоинта /{slug}
async def test_redirect_to_url(ac: AsyncClient):
    # сначала генерируем короткий slug
    slug_result = await ac.post("/short_url", json={"long_url": "https://my-site.com"})
    assert slug_result.status_code == 200
    slug = slug_result.json()["data"]

    # затем проверяем перенаправление
    result = await ac.get(f"/{slug}")
    assert result.status_code == 302
