import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import Column, DateTime, Enum as SQLEnum, ForeignKey, String, Text, JSON

from app.db.base import Base
from app.db.types import GUID, StringArray


class InteractionType(str, Enum):
    MEETING = "meeting"
    CALL = "call"
    EMAIL = "email"
    CONFERENCE = "conference"
    SAMPLE_DROP = "sample_drop"


class Channel(str, Enum):
    IN_PERSON = "in_person"
    PHONE = "phone"
    VIDEO = "video"
    EMAIL = "email"


class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class Source(str, Enum):
    FORM = "form"
    AI_ASSISTANT = "ai_assistant"


class Status(str, Enum):
    DRAFT = "draft"
    LOGGED = "logged"


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    hcp_id = Column(GUID, ForeignKey("hcps.id"), nullable=False, index=True)
    user_id = Column(String(255), nullable=False)
    interaction_type = Column(SQLEnum(InteractionType), nullable=False)
    channel = Column(SQLEnum(Channel), nullable=False)
    interaction_date = Column(DateTime, nullable=False, index=True)
    subject = Column(String(500), nullable=False)
    notes = Column(Text, nullable=True)
    sentiment = Column(SQLEnum(Sentiment), nullable=True)
    products = Column(StringArray, nullable=True, default=list)
    follow_up_actions = Column(JSON, nullable=True, default=list)
    ai_summary = Column(Text, nullable=True)
    source = Column(SQLEnum(Source), nullable=False, default=Source.FORM)
    status = Column(SQLEnum(Status), nullable=False, default=Status.DRAFT)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Interaction(id={self.id}, hcp_id={self.hcp_id}, type={self.interaction_type})>"
