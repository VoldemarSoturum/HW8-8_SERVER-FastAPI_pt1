import pytest


@pytest.mark.anyio
async def test_search_filters(client):
    # создадим несколько объявлений
    ads = [
        {"title": "Продам RTX 4090", "description": "Новая", "price": "2500.00", "author": "Alice"},
        {"title": "Куплю RTX", "description": "Ищу 3080/3090", "price": "1200.00", "author": "Bob"},
        {"title": "Продам велосипед", "description": "Горный", "price": "300.00", "author": "Alice"},
    ]
    ids = []
    for a in ads:
        r = await client.post("/advertisement", json=a)
        assert r.status_code == 201
        ids.append(r.json()["id"])

    # q (общий поиск)
    r = await client.get("/advertisement", params={"q": "rtx"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 2
    assert any("RTX" in it["title"] or "rtx" in it["title"].lower() for it in items)

    # author filter
    r = await client.get("/advertisement", params={"author": "Alice"})
    assert r.status_code == 200
    items = r.json()
    assert len(items) >= 2
    assert all("alice" in it["author"].lower() for it in items)

    # price range
    r = await client.get("/advertisement", params={"price_from": "1000", "price_to": "2600"})
    assert r.status_code == 200
    items = r.json()
    assert all(1000 <= float(it["price"]) <= 2600 for it in items)

    # cleanup
    for ad_id in ids:
        await client.delete(f"/advertisement/{ad_id}")
