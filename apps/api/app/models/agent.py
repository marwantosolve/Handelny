import uuid

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base

DEFAULT_SYSTEM_PROMPT = (
    "You are a helpful customer support assistant. Answer only using the "
    "information provided in the context below. If the answer is not in the "
    "context, say you don't have that information instead of guessing."
)
DEFAULT_FALLBACK_MESSAGE = (
    "I don't have information about that in my knowledge base yet. "
    "Could you rephrase, or contact support directly?"
)


class Agent(Base):
    __tablename__ = "agents"

    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    kb_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("knowledge_bases.id", ondelete="SET NULL"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    system_prompt: Mapped[str] = mapped_column(Text, default=DEFAULT_SYSTEM_PROMPT, nullable=False)
    welcome_message: Mapped[str] = mapped_column(
        String(500), default="Hi! How can I help you today?", nullable=False
    )
    fallback_message: Mapped[str] = mapped_column(
        String(500), default=DEFAULT_FALLBACK_MESSAGE, nullable=False
    )
    language: Mapped[str] = mapped_column(String(10), default="auto", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
