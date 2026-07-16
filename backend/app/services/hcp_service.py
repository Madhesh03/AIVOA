from uuid import UUID
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.db.models import HCP
from app.repositories import HCPRepository
from app.schemas.hcp import HCPCreate, HCPUpdate, HCPResponse


class HCPService:
    def __init__(self, session: AsyncSession):
        self.repository = HCPRepository(session)
        self.session = session

    async def get_hcp(self, hcp_id: UUID) -> HCPResponse:
        hcp = await self.repository.get_by_id(hcp_id)
        if not hcp:
            raise NotFoundError("HCP", hcp_id)
        return HCPResponse.model_validate(hcp)

    async def get_or_create_by_name(self, name: str) -> HCP:
        existing = await self.repository.get_by_name(name)
        if existing:
            return existing

        hcp = await self.repository.create(name=name)
        await self.repository.commit()
        return hcp

    async def create_hcp(self, data: HCPCreate) -> HCPResponse:
        hcp = await self.repository.create(**data.model_dump())
        await self.repository.commit()
        return HCPResponse.model_validate(hcp)

    async def update_hcp(self, hcp_id: UUID, data: HCPUpdate) -> HCPResponse:
        hcp = await self.repository.get_by_id(hcp_id)
        if not hcp:
            raise NotFoundError("HCP", hcp_id)

        update_data = data.model_dump(exclude_unset=True)
        updated_hcp = await self.repository.update(hcp, **update_data)
        await self.repository.commit()
        return HCPResponse.model_validate(updated_hcp)

    async def delete_hcp(self, hcp_id: UUID) -> None:
        hcp = await self.repository.get_by_id(hcp_id)
        if not hcp:
            raise NotFoundError("HCP", hcp_id)

        await self.repository.delete(hcp)
        await self.repository.commit()

    async def list_hcps(self, skip: int = 0, limit: int = 10) -> tuple[list[HCPResponse], int]:
        hcps, total = await self.repository.get_all_paginated(skip, limit)
        return [HCPResponse.model_validate(hcp) for hcp in hcps], total

    async def search_hcps(
        self, query: str, skip: int = 0, limit: int = 10
    ) -> tuple[list[HCPResponse], int]:
        hcps, total = await self.repository.search(query, skip, limit)
        return [HCPResponse.model_validate(hcp) for hcp in hcps], total
