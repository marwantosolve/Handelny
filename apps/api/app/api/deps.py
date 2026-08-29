"""Shared FastAPI dependencies: DB session, current user, current org."""
import uuid
from dataclasses import dataclass

from fastapi import Depends, Header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.exceptions import UnauthorizedError
from app.core.security import decode_access_token
from app.models.membership import Membership
from app.models.organization import Organization
from app.models.user import User


@dataclass
class CurrentPrincipal:
    """The authenticated user, scoped to the org encoded in their access token."""

    user: User
    organization: Organization
    role: str


async def get_current_principal(
    authorization: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
) -> CurrentPrincipal:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise UnauthorizedError("Missing or invalid Authorization header")

    token = authorization.split(" ", 1)[1].strip()
    payload = decode_access_token(token)
    if not payload:
        raise UnauthorizedError("Invalid or expired token")

    try:
        user_id = uuid.UUID(payload["sub"])
        org_id = uuid.UUID(payload["org_id"])
    except (KeyError, ValueError) as exc:
        raise UnauthorizedError("Malformed token payload") from exc

    user = await db.get(User, user_id)
    if not user or not user.is_active:
        raise UnauthorizedError("User not found or inactive")

    membership = (
        await db.execute(
            select(Membership).where(Membership.user_id == user_id, Membership.org_id == org_id)
        )
    ).scalar_one_or_none()
    if not membership:
        raise UnauthorizedError("User does not belong to this organization")

    organization = await db.get(Organization, org_id)
    if not organization:
        raise UnauthorizedError("Organization not found")

    return CurrentPrincipal(user=user, organization=organization, role=membership.role)
