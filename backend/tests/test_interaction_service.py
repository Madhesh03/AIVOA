from datetime import datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.db.models import Channel, InteractionType, Sentiment, Source, Status
from app.schemas.hcp import HCPCreate
from app.schemas.interaction import InteractionCreate
from app.services.hcp_service import HCPService
from app.services.interaction_service import InteractionService


async def _make_hcp(session: AsyncSession) -> str:
    hcp = await HCPService(session).create_hcp(HCPCreate(name="Dr. Flow", specialty="Cardiology"))
    return hcp.id


def _draft_payload(hcp_id) -> InteractionCreate:
    return InteractionCreate(
        hcp_id=hcp_id,
        user_id="tester",
        interaction_type=InteractionType.MEETING,
        channel=Channel.IN_PERSON,
        interaction_date=datetime(2026, 1, 1, 10, 0),
        subject="Cardio-Z discussion",
        notes="Positive response",
        sentiment=Sentiment.POSITIVE,
        products=["Cardio-Z"],
    )


@pytest.mark.asyncio
async def test_ai_source_interaction_created_as_draft(test_db: AsyncSession):
    service = InteractionService(test_db)
    hcp_id = await _make_hcp(test_db)

    result = await service.create_interaction(
        _draft_payload(hcp_id), source=Source.AI_ASSISTANT, status=Status.DRAFT
    )

    assert result.source == Source.AI_ASSISTANT
    assert result.status == Status.DRAFT
    assert result.products == ["Cardio-Z"]


@pytest.mark.asyncio
async def test_confirm_promotes_draft_to_logged(test_db: AsyncSession):
    service = InteractionService(test_db)
    hcp_id = await _make_hcp(test_db)

    draft = await service.create_interaction(
        _draft_payload(hcp_id), source=Source.AI_ASSISTANT, status=Status.DRAFT
    )
    confirmed = await service.confirm_interaction(draft.id)

    assert confirmed.id == draft.id
    assert confirmed.status == Status.LOGGED


@pytest.mark.asyncio
async def test_confirm_missing_interaction_raises(test_db: AsyncSession):
    from uuid import uuid4

    service = InteractionService(test_db)
    with pytest.raises(NotFoundError):
        await service.confirm_interaction(uuid4())


@pytest.mark.asyncio
async def test_list_reflects_created_interactions(test_db: AsyncSession):
    service = InteractionService(test_db)
    hcp_id = await _make_hcp(test_db)

    for _ in range(3):
        await service.create_interaction(_draft_payload(hcp_id))

    items, total = await service.list_interactions(skip=0, limit=10)
    assert total == 3
    assert len(items) == 3
