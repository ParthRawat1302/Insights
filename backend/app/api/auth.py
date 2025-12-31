import token
from fastapi import APIRouter, HTTPException, Depends, status
from datetime import timedelta

from app.models.user import (
    UserRegisterRequest,
    UserLoginRequest,
    UserResponse
)
from app.services.user_service import (
    create_user,
    authenticate_user,
    get_user_by_id
)
from app.core.security import (
    create_access_token,
    decode_access_token
)
from app.core.config import settings
from app.core.dependencies import get_current_user

from pydantic import BaseModel

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserRegisterRequest):
    print("Registering user with email:", payload.email)
    try:
        user = create_user(payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        )

    return UserResponse(
        _id=str(user["_id"]),
        email=user["email"],
        name=user.get("profile", {}).get("name"),
        is_active=user["is_active"],
        created_at=user["created_at"]
    )


@router.post("/login", response_model=TokenResponse)
def login_user(payload: UserLoginRequest):
    user = authenticate_user(payload.email, payload.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    access_token = create_access_token(
        subject=str(user["_id"]),
        expires_delta=timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: dict = Depends(get_current_user)):
    return UserResponse(
        _id=str(current_user["_id"]),
        email=current_user["email"],
        name=current_user.get("profile", {}).get("name"),
        is_active=current_user["is_active"],
        created_at=current_user["created_at"]
    )

