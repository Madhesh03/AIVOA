from datetime import datetime
from uuid import UUID
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession


def _to_naive_datetime(dt: datetime) -> datetime:
    """Convert timezone-aware datetime to naive datetime (UTC)."""
    if dt and dt.tzinfo is not None:
        return dt.replace(tzinfo=None)
    return dt

from app.core.exceptions import NotFoundError
from app.db.models import Interaction, InteractionType, Source, Status
from app.repositories import InteractionRepository
from app.schemas.interaction import (
    InteractionCreate,
    InteractionUpdate,
    InteractionResponse,
)


class InteractionService:
    def __init__(self, session: AsyncSession):
        self.repository = InteractionRepository(session)
        self.session = session

    async def get_interaction(self, interaction_id: UUID) -> InteractionResponse:
        interaction = await self.repository.get_by_id(interaction_id)
        if not interaction:
            raise NotFoundError("Interaction", interaction_id)
        return InteractionResponse.model_validate(interaction)

    async def create_interaction(
        self, data: InteractionCreate, source: Source = Source.FORM, status: Status = Status.DRAFT
    ) -> InteractionResponse:
        create_data = data.model_dump()
        create_data["source"] = source
        create_data["status"] = status
        interaction = await self.repository.create(**create_data)
        await self.repository.commit()
        return InteractionResponse.model_validate(interaction)

    async def update_interaction(
        self, interaction_id: UUID, data: InteractionUpdate
    ) -> InteractionResponse:
        interaction = await self.repository.get_by_id(interaction_id)
        if not interaction:
            raise NotFoundError("Interaction", interaction_id)

        update_data = data.model_dump(exclude_unset=True)
        # Convert timezone-aware datetimes to naive for database compatibility
        if "interaction_date" in update_data and update_data["interaction_date"]:
            update_data["interaction_date"] = _to_naive_datetime(update_data["interaction_date"])
        updated = await self.repository.update(interaction, **update_data)
        await self.repository.commit()
        return InteractionResponse.model_validate(updated)

    async def confirm_interaction(self, interaction_id: UUID) -> InteractionResponse:
        interaction = await self.repository.get_by_id(interaction_id)
        if not interaction:
            raise NotFoundError("Interaction", interaction_id)

        interaction.status = Status.LOGGED
        await self.repository.commit()
        return InteractionResponse.model_validate(interaction)

    async def delete_interaction(self, interaction_id: UUID) -> None:
        interaction = await self.repository.get_by_id(interaction_id)
        if not interaction:
            raise NotFoundError("Interaction", interaction_id)

        await self.repository.delete(interaction)
        await self.repository.commit()

    async def list_interactions(
        self, skip: int = 0, limit: int = 10
    ) -> tuple[list[InteractionResponse], int]:
        interactions, total = await self.repository.get_all_paginated(skip, limit)
        return [InteractionResponse.model_validate(i) for i in interactions], total

    async def list_interactions_by_hcp(
        self, hcp_id: UUID, skip: int = 0, limit: int = 10
    ) -> tuple[list[InteractionResponse], int]:
        interactions, total = await self.repository.get_by_hcp_id(hcp_id, skip, limit)
        return [InteractionResponse.model_validate(i) for i in interactions], total

    async def search_interactions(
        self,
        query: str = "",
        hcp_id: Optional[UUID] = None,
        interaction_type: Optional[InteractionType] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 10,
    ) -> tuple[list[InteractionResponse], int]:
        interactions, total = await self.repository.search(
            query=query,
            hcp_id=hcp_id,
            interaction_type=interaction_type,
            from_date=from_date,
            to_date=to_date,
            skip=skip,
            limit=limit,
        )
        return [InteractionResponse.model_validate(i) for i in interactions], total

    async def add_ai_summary(self, interaction_id: UUID, summary: str) -> InteractionResponse:
        interaction = await self.repository.get_by_id(interaction_id)
        if not interaction:
            raise NotFoundError("Interaction", interaction_id)

        interaction.ai_summary = summary
        await self.repository.commit()
        return InteractionResponse.model_validate(interaction)

    async def add_followup_actions(
        self, interaction_id: UUID, actions: list[dict]
    ) -> InteractionResponse:
        interaction = await self.repository.get_by_id(interaction_id)
        if not interaction:
            raise NotFoundError("Interaction", interaction_id)

        interaction.follow_up_actions = actions
        await self.repository.commit()
        return InteractionResponse.model_validate(interaction)
