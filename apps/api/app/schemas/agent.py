"""Request/response schemas for agent endpoints."""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AgentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    system_prompt: str | None = None
    welcome_message: str | None = None
    fallback_message: str | None = None
    language: str | None = None
    kb_id: uuid.UUID | None = None


class AgentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    system_prompt: str | None = None
    welcome_message: str | None = None
    fallback_message: str | None = None
    language: str | None = None
    kb_id: uuid.UUID | None = None
    is_active: bool | None = None


class AgentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    org_id: uuid.UUID
    kb_id: uuid.UUID | None
    name: str
    system_prompt: str
    welcome_message: str
    fallback_message: str
    language: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
