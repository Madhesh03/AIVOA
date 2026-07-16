from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.schemas.hcp import HCPCreate, HCPResponse, HCPUpdate
from app.services.hcp_service import HCPService

router = APIRouter()


async def get_hcp_service(session: AsyncSession = Depends(get_db_session)) -> HCPService:
    return HCPService(session)


@router.post("/hcps", response_model=HCPResponse, status_code=201)
async def create_hcp(
    data: HCPCreate,
    service: HCPService = Depends(get_hcp_service),
) -> HCPResponse:
    return await service.create_hcp(data)


@router.get("/hcps", response_model=dict)
async def list_hcps(
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    service: HCPService = Depends(get_hcp_service),
) -> dict:
    hcps, total = await service.list_hcps(skip, limit)
    return {
        "total": total,
        "limit": limit,
        "offset": skip,
        "items": hcps,
    }


# NOTE: /search must precede the dynamic /{hcp_id} route so FastAPI does not
# match "search" as a UUID path param (which would 422 the autocomplete).
@router.get("/hcps/search", response_model=dict)
async def search_hcps(
    q: str = Query(..., min_length=1),
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    service: HCPService = Depends(get_hcp_service),
) -> dict:
    hcps, total = await service.search_hcps(q, skip, limit)
    return {
        "total": total,
        "limit": limit,
        "offset": skip,
        "items": hcps,
    }


@router.get("/hcps/{hcp_id}", response_model=HCPResponse)
async def get_hcp(
    hcp_id: UUID,
    service: HCPService = Depends(get_hcp_service),
) -> HCPResponse:
    return await service.get_hcp(hcp_id)


@router.patch("/hcps/{hcp_id}", response_model=HCPResponse)
async def update_hcp(
    hcp_id: UUID,
    data: HCPUpdate,
    service: HCPService = Depends(get_hcp_service),
) -> HCPResponse:
    return await service.update_hcp(hcp_id, data)


@router.delete("/hcps/{hcp_id}", status_code=204)
async def delete_hcp(
    hcp_id: UUID,
    service: HCPService = Depends(get_hcp_service),
) -> None:
    await service.delete_hcp(hcp_id)
