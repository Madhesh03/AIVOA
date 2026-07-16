from typing import Optional
from uuid import UUID

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import HCP
from app.repositories.base import BaseRepository


class HCPRepository(BaseRepository[HCP]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, HCP)

    async def get_by_name(self, name: str) -> Optional[HCP]:
        stmt = select(self.model).where(self.model.name.ilike(f"%{name}%")).limit(1)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[HCP]:
        stmt = select(self.model).where(self.model.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def search(self, query: str, skip: int = 0, limit: int = 10) -> tuple[list[HCP], int]:
        search_pattern = f"%{query}%"
        stmt = (
            select(self.model)
            .where(
                or_(
                    self.model.name.ilike(search_pattern),
                    self.model.specialty.ilike(search_pattern),
                    self.model.organization.ilike(search_pattern),
                )
            )
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        items = result.scalars().all()

        count_stmt = select(self.model).where(
            or_(
                self.model.name.ilike(search_pattern),
                self.model.specialty.ilike(search_pattern),
                self.model.organization.ilike(search_pattern),
            )
        )
        count_result = await self.session.execute(count_stmt)
        total = len(count_result.scalars().all())

        return items, total

    async def get_all_paginated(
        self, skip: int = 0, limit: int = 10
    ) -> tuple[list[HCP], int]:
        items = await self.get_all(skip, limit)
        count_stmt = select(self.model)
        count_result = await self.session.execute(count_stmt)
        total = len(count_result.scalars().all())
        return items, total
