from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.models.user import UserProfileResponse

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.get("/profile", response_model=UserProfileResponse)
def get_profile(current_user: dict = Depends(get_current_user)):
    return UserProfileResponse(
        id=str(current_user["_id"]),
        email=current_user["email"],
        name=current_user.get("profile", {}).get("name"),
        is_active=current_user["is_active"],
        created_at=current_user["created_at"],
        stats=current_user.get("stats", {})
    )
