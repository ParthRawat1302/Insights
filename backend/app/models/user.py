from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str = Field(alias="_id")
    email: EmailStr
    name: Optional[str] = None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(populate_by_name=True)

class UserInDB(BaseModel):
    email: EmailStr
    hashed_password: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    profile: dict = {}
    stats: dict = {}

class UserProfileResponse(BaseModel):
    id: str
    email: EmailStr
    name: Optional[str]
    is_active: bool
    created_at: datetime

    stats: dict
