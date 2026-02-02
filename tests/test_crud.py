import pytest


@pytest.mark.anyio
async def test_crud_flow(client):
    # CREATE
    payload = {
        "title": "Продам ноутбук",
        "description": "Отличное состояние",
        "price": "999.90",
        "author": "Voldemar",
    }
    r = await client.post("/advertisement", json=payload)
    assert r.status_code == 201
    data = r.json()
    ad_id = data["id"]
    assert data["title"] == payload["title"]
    assert data["author"] == payload["author"]
    assert "created_at" in data

    # GET
    r = await client.get(f"/advertisement/{ad_id}")
    assert r.status_code == 200
    assert r.json()["id"] == ad_id

    # PATCH
    patch = {"price": "899.50", "description": "Срочно"}
    r = await client.patch(f"/advertisement/{ad_id}", json=patch)
    assert r.status_code == 200
    patched = r.json()
    assert patched["price"] == "899.50"
    assert patched["description"] == "Срочно"

    # DELETE
    r = await client.delete(f"/advertisement/{ad_id}")
    assert r.status_code == 200
    assert r.json()["status"] == "deleted"

    # GET after delete => 404
    r = await client.get(f"/advertisement/{ad_id}")
    assert r.status_code == 404
