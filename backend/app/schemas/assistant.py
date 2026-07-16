from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.interaction import InteractionDraft


class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    user_id: str


class ToolResult(BaseModel):
    tool: str
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    form_prefill: Optional[InteractionDraft] = None
    interaction_id: Optional[UUID] = None


class StreamEvent(BaseModel):
    type: str = Field(..., pattern="^(token|tool_start|tool_result|done|error)$")
    data: Any


class ChatResponse(BaseModel):
    conversation_id: str
    messages: list[ChatMessage]
