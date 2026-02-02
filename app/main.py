from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime
from decimal import Decimal
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.crud import AdvertisementCRUD
from app.db import close_engine, get_db
from app.schemas import AdvertisementCreate, AdvertisementOut, AdvertisementUpdate

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup (ничего не нужно)
    yield
    # shutdown
    await close_engine()


app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)


@app.post("/advertisement", response_model=AdvertisementOut, status_code=201)
async def create_advertisement(payload: AdvertisementCreate, db: AsyncSession = Depends(get_db)):
    return await AdvertisementCRUD(db).create(
        title=payload.title,
        description=payload.description,
        price=payload.price,
        author=payload.author,
    )


@app.patch("/advertisement/{advertisement_id}", response_model=AdvertisementOut)
async def patch_advertisement(
    advertisement_id: int,
    payload: AdvertisementUpdate,
    db: AsyncSession = Depends(get_db),
):
    ad = await AdvertisementCRUD(db).patch(
        advertisement_id,
        title=payload.title,
        description=payload.description,
        price=payload.price,
        author=payload.author,
    )
    if ad is None:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return ad


@app.delete("/advertisement/{advertisement_id}")
async def delete_advertisement(advertisement_id: int, db: AsyncSession = Depends(get_db)):
    ok = await AdvertisementCRUD(db).delete(advertisement_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return {"status": "deleted", "id": advertisement_id}


@app.get("/advertisement/{advertisement_id}", response_model=AdvertisementOut)
async def get_advertisement(advertisement_id: int, db: AsyncSession = Depends(get_db)):
    ad = await AdvertisementCRUD(db).get(advertisement_id)
    if ad is None:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return ad


@app.get("/advertisement", response_model=list[AdvertisementOut])
async def search_advertisements(
    db: AsyncSession = Depends(get_db),
    title: Optional[str] = None,
    description: Optional[str] = None,
    author: Optional[str] = None,
    q: Optional[str] = None,
    price_from: Optional[Decimal] = Query(default=None, gt=0),
    price_to: Optional[Decimal] = Query(default=None, gt=0),
    created_from: Optional[datetime] = None,
    created_to: Optional[datetime] = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    return await AdvertisementCRUD(db).search(
        title=title,
        description=description,
        author=author,
        q=q,
        price_from=price_from,
        price_to=price_to,
        created_from=created_from,
        created_to=created_to,
        limit=limit,
        offset=offset,
    )
