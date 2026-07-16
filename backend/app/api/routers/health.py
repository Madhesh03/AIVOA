from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session

router = APIRouter()


@router.get("/health")
async def health_check(session: AsyncSession = Depends(get_db_session)) -> dict:
    try:
        await session.execute("SELECT 1")
        return {
            "status": "healthy",
            "service": "hcp-crm-backend",
            "database": "connected",
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "hcp-crm-backend",
            "database": "disconnected",
            "error": str(e),
        }
