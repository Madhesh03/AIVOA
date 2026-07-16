from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.db.models.interaction import Channel, InteractionType, Sentiment, Source, Status


class FollowUpAction(BaseModel):
    action: str
    due_date: Optional[datetime] = None
    priority: str = "medium"
    done: bool = False


class InteractionBase(BaseModel):
    interaction_type: InteractionType
    channel: Channel
    interaction_date: datetime
    subject: str = Field(..., min_length=1, max_length=500)
    notes: Optional[str] = None
    sentiment: Optional[Sentiment] = None
    products: Optional[list[str]] = Field(default_factory=list)
    follow_up_actions: Optional[list[dict[str, Any]]] = Field(default_factory=list)


class InteractionCreate(InteractionBase):
    hcp_id: UUID
    user_id: str


class InteractionUpdate(BaseModel):
    interaction_type: Optional[InteractionType] = None
    channel: Optional[Channel] = None
    interaction_date: Optional[datetime] = None
    subject: Optional[str] = Field(None, min_length=1, max_length=500)
    notes: Optional[str] = None
    sentiment: Optional[Sentiment] = None
    products: Optional[list[str]] = None
    follow_up_actions: Optional[list[dict[str, Any]]] = None


class InteractionResponse(InteractionBase):
    id: UUID
    hcp_id: UUID
    user_id: str
    source: Source
    status: Status
    ai_summary: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @field_validator("follow_up_actions", mode="before")
    @classmethod
    def validate_follow_up_actions(cls, v: Any) -> Optional[list[dict[str, Any]]]:
        """Handle follow_up_actions that might come as string or malformed JSON."""
        if v is None:
            return []
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            try:
                import json
                parsed = json.loads(v)
                return parsed if isinstance(parsed, list) else []
            except (json.JSONDecodeError, ValueError):
                return []
        return []


class InteractionListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[InteractionResponse]


class InteractionDraft(BaseModel):
    hcp_id: Optional[UUID] = None
    hcp_name: Optional[str] = None
    interaction_type: Optional[InteractionType] = None
    channel: Optional[Channel] = None
    interaction_date: Optional[datetime] = None
    subject: Optional[str] = None
    notes: Optional[str] = None
    sentiment: Optional[Sentiment] = None
    products: Optional[list[str]] = Field(default_factory=list)
    follow_up_actions: Optional[list[dict[str, Any]]] = Field(default_factory=list)
