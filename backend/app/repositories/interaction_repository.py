from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import select, and_, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Interaction, Status, InteractionType, Channel, Source
from app.repositories.base import BaseRepository


class InteractionRepository(BaseRepository[Interaction]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Interaction)

    async def get_by_hcp_id(
        self, hcp_id: UUID, skip: int = 0, limit: int = 10
    ) -> tuple[list[Interaction], int]:
        stmt = (
            select(self.model)
            .where(self.model.hcp_id == hcp_id)
            .order_by(desc(self.model.interaction_date))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        items = result.scalars().all()

        count_stmt = select(func.count(self.model.id)).where(self.model.hcp_id == hcp_id)
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar() or 0

        return items, total

    async def search(
        self,
        query: str,
        hcp_id: Optional[UUID] = None,
        interaction_type: Optional[InteractionType] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 10,
    ) -> tuple[list[Interaction], int]:
        conditions = []

        if hcp_id:
            conditions.append(self.model.hcp_id == hcp_id)

        if interaction_type:
            conditions.append(self.model.interaction_type == interaction_type)

        if from_date:
            conditions.append(self.model.interaction_date >= from_date)

        if to_date:
            conditions.append(self.model.interaction_date <= to_date)

        if query:
            conditions.append(
                (self.model.subject.ilike(f"%{query}%"))
                | (self.model.notes.ilike(f"%{query}%"))
            )

        stmt = (
            select(self.model)
            .where(and_(*conditions) if conditions else True)
            .order_by(desc(self.model.interaction_date))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        items = result.scalars().all()

        count_stmt = select(func.count(self.model.id)).where(
            and_(*conditions) if conditions else True
        )
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar() or 0

        return items, total

    async def get_all_paginated(
        self, skip: int = 0, limit: int = 10
    ) -> tuple[list[Interaction], int]:
        stmt = (
            select(self.model)
            .order_by(desc(self.model.interaction_date))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        items = result.scalars().all()

        count_stmt = select(func.count(self.model.id))
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar() or 0

        return items, total

    async def get_by_source(
        self, source: Source, skip: int = 0, limit: int = 10
    ) -> tuple[list[Interaction], int]:
        stmt = (
            select(self.model)
            .where(self.model.source == source)
            .order_by(desc(self.model.interaction_date))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        items = result.scalars().all()

        count_stmt = select(func.count(self.model.id)).where(self.model.source == source)
        count_result = await self.session.execute(count_stmt)
        total = count_result.scalar() or 0

        return items, total
