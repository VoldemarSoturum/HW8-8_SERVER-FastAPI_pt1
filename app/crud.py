from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import and_, delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Advertisement


class AdvertisementCRUD:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, *, title: str, description: str, price: Decimal, author: str) -> Advertisement:
        ad = Advertisement(title=title, description=description, price=price, author=author)
        self.db.add(ad)
        await self.db.commit()
        await self.db.refresh(ad)
        return ad

    async def get(self, ad_id: int) -> Optional[Advertisement]:
        res = await self.db.execute(select(Advertisement).where(Advertisement.id == ad_id))
        return res.scalar_one_or_none()

    async def delete(self, ad_id: int) -> bool:
        res = await self.db.execute(delete(Advertisement).where(Advertisement.id == ad_id).returning(Advertisement.id))
        deleted = res.scalar_one_or_none()
        if deleted is None:
            return False
        await self.db.commit()
        return True

    async def patch(
        self,
        ad_id: int,
        *,
        title: Optional[str] = None,
        description: Optional[str] = None,
        price: Optional[Decimal] = None,
        author: Optional[str] = None,
    ) -> Optional[Advertisement]:
        values = {}
        if title is not None:
            values["title"] = title
        if description is not None:
            values["description"] = description
        if price is not None:
            values["price"] = price
        if author is not None:
            values["author"] = author

        if not values:
            # ничего обновлять
            return await self.get(ad_id)

        stmt = (
            update(Advertisement)
            .where(Advertisement.id == ad_id)
            .values(**values)
            .returning(Advertisement)
        )
        res = await self.db.execute(stmt)
        updated = res.scalar_one_or_none()
        if updated is None:
            return None
        await self.db.commit()
        return updated

    async def search(
        self,
        *,
        title: Optional[str] = None,
        description: Optional[str] = None,
        author: Optional[str] = None,
        q: Optional[str] = None,
        price_from: Optional[Decimal] = None,
        price_to: Optional[Decimal] = None,
        created_from: Optional[datetime] = None,
        created_to: Optional[datetime] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Advertisement]:
        filters = []

        if title:
            filters.append(Advertisement.title.ilike(f"%{title}%"))
        if description:
            filters.append(Advertisement.description.ilike(f"%{description}%"))
        if author:
            filters.append(Advertisement.author.ilike(f"%{author}%"))

        # q — общий поиск по title/description/author
        if q:
            filters.append(
                (Advertisement.title.ilike(f"%{q}%"))
                | (Advertisement.description.ilike(f"%{q}%"))
                | (Advertisement.author.ilike(f"%{q}%"))
            )

        if price_from is not None:
            filters.append(Advertisement.price >= price_from)
        if price_to is not None:
            filters.append(Advertisement.price <= price_to)

        if created_from is not None:
            filters.append(Advertisement.created_at >= created_from)
        if created_to is not None:
            filters.append(Advertisement.created_at <= created_to)

        stmt = select(Advertisement).order_by(Advertisement.created_at.desc())

        if filters:
            stmt = stmt.where(and_(*filters))

        stmt = stmt.limit(min(max(limit, 1), 200)).offset(max(offset, 0))

        res = await self.db.execute(stmt)
        return list(res.scalars().all())
