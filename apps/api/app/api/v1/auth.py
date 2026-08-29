"""Authentication endpoints: register, login, current-user info."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentPrincipal, get_current_principal
from app.core.db import get_db
from app.core.security import create_access_token
from app.schemas.auth import (
    LoginRequest,
    MeResponse,
    OrganizationOut,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
    UserOut,
)
from app.services import auth as auth_service

router = APIRouter()


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)) -> RegisterResponse:
    user, organization, _membership = await auth_service.register(
        db,
        email=body.email,
        password=body.password,
        full_name=body.full_name,
        org_name=body.org_name,
    )
    access_token = create_access_token(user_id=user.id, org_id=organization.id)
    return RegisterResponse(
        access_token=access_token,
        user=UserOut.model_validate(user),
        organization=OrganizationOut.model_validate(organization),
    )


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    user, membership = await auth_service.authenticate(db, email=body.email, password=body.password)
    access_token = create_access_token(user_id=user.id, org_id=membership.org_id)
    return TokenResponse(access_token=access_token)


@router.get("/me", response_model=MeResponse)
async def me(principal: CurrentPrincipal = Depends(get_current_principal)) -> MeResponse:
    return MeResponse(
        user=UserOut.model_validate(principal.user),
        organization=OrganizationOut.model_validate(principal.organization),
        role=principal.role,
    )
