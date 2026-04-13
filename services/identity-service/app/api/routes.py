"""Identity Service API routes."""

from __future__ import annotations

from datetime import UTC, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from passlib.hash import bcrypt

from naql_common.auth import AuthManager, Permission, UserRole

from ..core.config import settings
from ..core.deps import get_current_user, require_permission
from ..schemas.user import (
    KYCVerifyRequest,
    TokenResponse,
    UserListResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
    UserUpdateRequest,
)

router = APIRouter(prefix="/api/v1", tags=["identity"])

auth_manager = AuthManager(settings.JWT_SECRET_KEY, settings.JWT_ALGORITHM)

# In-memory store for demo (replace with real DB in production)
_users_db: dict[str, dict] = {}


@router.post("/auth/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(request: UserRegisterRequest) -> TokenResponse:
    """Register a new user account."""
    # Check for duplicate email
    for user in _users_db.values():
        if user["email"] == request.email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )

    import uuid
    from datetime import datetime

    user_id = str(uuid.uuid4())
    password_hash = bcrypt.hash(request.password)

    user_data = {
        "id": user_id,
        "email": request.email,
        "phone": request.phone,
        "password_hash": password_hash,
        "full_name": request.full_name,
        "role": request.role,
        "region_code": request.region_code,
        "national_id": request.national_id,
        "kyc_status": "pending",
        "reputation_score": 5.00,
        "is_active": True,
        "created_at": datetime.now(UTC),
    }
    _users_db[user_id] = user_data

    role = UserRole(request.role)
    access_token = auth_manager.create_access_token(
        user_id=user_id,
        role=role,
        region=request.region_code,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = auth_manager.create_refresh_token(
        user_id=user_id,
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )

    return TokenResponse(
        user_id=user_id,
        access_token=access_token,
        refresh_token=refresh_token,
        role=request.role,
        region_code=request.region_code,
    )


@router.post("/auth/login", response_model=TokenResponse)
async def login(request: UserLoginRequest) -> TokenResponse:
    """Authenticate a user and return tokens."""
    user = None
    for u in _users_db.values():
        if u["email"] == request.email:
            user = u
            break

    if user is None or not bcrypt.verify(request.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    role = UserRole(user["role"])
    access_token = auth_manager.create_access_token(
        user_id=user["id"],
        role=role,
        region=user["region_code"],
    )
    refresh_token = auth_manager.create_refresh_token(user_id=user["id"])

    return TokenResponse(
        user_id=user["id"],
        access_token=access_token,
        refresh_token=refresh_token,
        role=user["role"],
        region_code=user["region_code"],
    )


@router.get("/users/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: Annotated[dict, Depends(get_current_user)],
) -> UserResponse:
    """Get the current authenticated user's profile."""
    user = _users_db.get(current_user.sub)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return UserResponse(**{k: v for k, v in user.items() if k != "password_hash"})


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str) -> UserResponse:
    """Get a user by ID."""
    user = _users_db.get(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return UserResponse(**{k: v for k, v in user.items() if k != "password_hash"})


@router.patch("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    request: UserUpdateRequest,
    _current_user: Annotated[dict, Depends(get_current_user)],
) -> UserResponse:
    """Update a user's profile."""
    user = _users_db.get(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    update_data = request.model_dump(exclude_unset=True)
    user.update(update_data)

    return UserResponse(**{k: v for k, v in user.items() if k != "password_hash"})


@router.post("/users/{user_id}/kyc", response_model=UserResponse)
async def verify_kyc(
    user_id: str,
    request: KYCVerifyRequest,
    _current_user: Annotated[dict, Depends(require_permission(Permission.USERS_WRITE))],
) -> UserResponse:
    """Verify or reject a user's KYC status. Requires admin permission."""
    user = _users_db.get(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user["kyc_status"] = request.kyc_status

    return UserResponse(**{k: v for k, v in user.items() if k != "password_hash"})


@router.get("/users", response_model=UserListResponse)
async def list_users(
    page: int = 1,
    page_size: int = 20,
    role: str | None = None,
    region_code: str | None = None,
) -> UserListResponse:
    """List users with pagination and filtering."""
    users = list(_users_db.values())

    if role:
        users = [u for u in users if u["role"] == role]
    if region_code:
        users = [u for u in users if u["region_code"] == region_code]

    total = len(users)
    start = (page - 1) * page_size
    end = start + page_size
    page_users = users[start:end]

    return UserListResponse(
        users=[
            UserResponse(**{k: v for k, v in u.items() if k != "password_hash"}) for u in page_users
        ],
        total=total,
        page=page,
        page_size=page_size,
        has_next=end < total,
    )
