from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.services import HCPService, InteractionService


async def get_hcp_service(session: AsyncSession = None) -> HCPService:
    if session is None:
        async for session in get_db_session():
            break
    return HCPService(session)


async def get_interaction_service(session: AsyncSession = None) -> InteractionService:
    if session is None:
        async for session in get_db_session():
            break
    return InteractionService(session)
