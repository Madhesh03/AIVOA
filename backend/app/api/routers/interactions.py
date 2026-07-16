from datetime import datetime
from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.db.models import InteractionType
from app.schemas.interaction import (
    InteractionCreate,
    InteractionListResponse,
    InteractionResponse,
    InteractionUpdate,
)
from app.services.interaction_service import InteractionService

router = APIRouter()


async def get_interaction_service(
    session: AsyncSession = Depends(get_db_session),
) -> InteractionService:
    return InteractionService(session)


@router.post("/interactions", response_model=InteractionResponse, status_code=201)
async def create_interaction(
    data: InteractionCreate,
    service: InteractionService = Depends(get_interaction_service),
) -> InteractionResponse:
    return await service.create_interaction(data)


@router.get("/interactions", response_model=InteractionListResponse)
async def list_interactions(
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    service: InteractionService = Depends(get_interaction_service),
) -> InteractionListResponse:
    interactions, total = await service.list_interactions(skip, limit)
    return InteractionListResponse(
        total=total,
        limit=limit,
        offset=skip,
        items=interactions,
    )


# NOTE: Static/sub-resource paths (/search, /hcp/{id}) MUST be declared before
# the dynamic /{interaction_id} route so FastAPI does not greedily match them
# as a UUID path param.
@router.get("/interactions/search", response_model=InteractionListResponse)
async def search_interactions(
    q: str = Query(""),
    hcp_id: Optional[UUID] = Query(None),
    interaction_type: Optional[InteractionType] = Query(None),
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None),
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    service: InteractionService = Depends(get_interaction_service),
) -> InteractionListResponse:
    interactions, total = await service.search_interactions(
        query=q,
        hcp_id=hcp_id,
        interaction_type=interaction_type,
        from_date=from_date,
        to_date=to_date,
        skip=skip,
        limit=limit,
    )
    return InteractionListResponse(
        total=total,
        limit=limit,
        offset=skip,
        items=interactions,
    )


@router.get("/interactions/hcp/{hcp_id}", response_model=InteractionListResponse)
async def list_interactions_by_hcp(
    hcp_id: UUID,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 10,
    service: InteractionService = Depends(get_interaction_service),
) -> InteractionListResponse:
    interactions, total = await service.list_interactions_by_hcp(hcp_id, skip, limit)
    return InteractionListResponse(
        total=total,
        limit=limit,
        offset=skip,
        items=interactions,
    )


@router.get("/interactions/{interaction_id}", response_model=InteractionResponse)
async def get_interaction(
    interaction_id: UUID,
    service: InteractionService = Depends(get_interaction_service),
) -> InteractionResponse:
    return await service.get_interaction(interaction_id)


@router.patch("/interactions/{interaction_id}", response_model=InteractionResponse)
async def update_interaction(
    interaction_id: UUID,
    data: InteractionUpdate,
    service: InteractionService = Depends(get_interaction_service),
) -> InteractionResponse:
    return await service.update_interaction(interaction_id, data)


@router.post("/interactions/{interaction_id}/confirm", response_model=InteractionResponse)
async def confirm_interaction(
    interaction_id: UUID,
    service: InteractionService = Depends(get_interaction_service),
) -> InteractionResponse:
    return await service.confirm_interaction(interaction_id)


@router.delete("/interactions/{interaction_id}", status_code=204)
async def delete_interaction(
    interaction_id: UUID,
    service: InteractionService = Depends(get_interaction_service),
) -> None:
    await service.delete_interaction(interaction_id)
