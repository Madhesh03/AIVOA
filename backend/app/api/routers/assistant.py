import json
import uuid
from typing import AsyncIterator

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.agent import create_agent_executor, AgentExecutor
from app.db.session import get_db_session
from app.schemas.assistant import ChatRequest

router = APIRouter()

# In-memory cache of conversation executors to maintain state across requests
_conversation_cache: dict[str, AgentExecutor] = {}


@router.post("/assistant/chat")
async def chat(
    request: ChatRequest,
    session: AsyncSession = Depends(get_db_session),
):
    async def event_generator() -> AsyncIterator[str]:
        conversation_id = request.conversation_id or str(uuid.uuid4())

        # Reuse existing executor if conversation exists, otherwise create new one
        if conversation_id in _conversation_cache:
            executor = _conversation_cache[conversation_id]
        else:
            executor = create_agent_executor(session, request.user_id)
            _conversation_cache[conversation_id] = executor

        try:
            async for event in executor.process_message(request.message):
                # default=str is a safety net for any UUID/datetime that slips
                # through a tool result unserialized.
                event_json = json.dumps(event, default=str)
                yield f"data: {event_json}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'data': {'error': str(e)}})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
