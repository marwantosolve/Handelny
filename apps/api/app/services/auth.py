"""Business logic for registration, login, and slug generation."""
import re
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.security import hash_password, verify_password
from app.models.membership import ROLE_OWNER, Membership
from app.models.organization import Organization
from app.models.user import User

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def slugify(text: str) -> str:
    slug = _SLUG_RE.sub("-", text.strip().lower()).strip("-")
    return slug or "org"


async def _unique_org_slug(db: AsyncSession, org_name: str) -> str:
    base_slug = slugify(org_name)
    slug = base_slug
    suffix = 2
    while True:
        existing = (
            await db.execute(select(Organization).where(Organization.slug == slug))
        ).scalar_one_or_none()
        if not existing:
            return slug
        slug = f"{base_slug}-{suffix}"
        suffix += 1


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    return (
        await db.execute(select(User).where(User.email == email))
    ).scalar_one_or_none()


async def register(
    db: AsyncSession, email: str, password: str, full_name: str, org_name: str
) -> tuple[User, Organization, Membership]:
    existing_user = await get_user_by_email(db, email)
    if existing_user:
        raise ConflictError("An account with this email already exists")

    slug = await _unique_org_slug(db, org_name)

    user = User(email=email, password_hash=hash_password(password), full_name=full_name)
    organization = Organization(name=org_name, slug=slug)
    db.add_all([user, organization])
    await db.flush()

    membership = Membership(user_id=user.id, org_id=organization.id, role=ROLE_OWNER)
    db.add(membership)
    await db.commit()

    return user, organization, membership


async def authenticate(db: AsyncSession, email: str, password: str) -> tuple[User, Membership]:
    user = await get_user_by_email(db, email)
    if not user or not user.is_active or not verify_password(password, user.password_hash):
        raise UnauthorizedError("Invalid email or password")

    membership = (
        await db.execute(
            select(Membership)
            .where(Membership.user_id == user.id)
            .order_by(Membership.created_at)
        )
    ).scalars().first()
    if not membership:
        raise UnauthorizedError("Invalid email or password")

    return user, membership


async def get_organization(db: AsyncSession, org_id: uuid.UUID) -> Organization | None:
    return await db.get(Organization, org_id)
