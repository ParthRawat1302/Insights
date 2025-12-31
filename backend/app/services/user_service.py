from typing import Optional
from datetime import datetime

from bson import ObjectId

from app.core.database import get_users_collection
from app.core.security import hash_password, verify_password
from app.models.user import UserRegisterRequest
from datetime import datetime
from app.core.database import get_insights_collection, get_datasets_collection



def get_user_by_email(email: str) -> Optional[dict]:
    users = get_users_collection()
    return users.find_one({"email": email})

def get_user_by_id(user_id: str) -> Optional[dict]:
    users = get_users_collection()
    try:
        return users.find_one({"_id": ObjectId(user_id)})
    except Exception:
        return None

def create_user(payload: UserRegisterRequest) -> dict:
    print("Creating user:", payload.email)
    users = get_users_collection()

    if users.find_one({"email": payload.email}):
        print("User already exists:", payload.email)
        raise ValueError("User already exists")

    user_doc = {
        "email": payload.email,
        "hashed_password": hash_password(payload.password),
        "is_active": True,
        "created_at": datetime.utcnow(),
        "profile": {
            "name": payload.name
        },
        "stats": {
            "datasets_uploaded": 0,
            "dashboards_created": 0,
            "insights_generated": 0
        }
    }

    result = users.insert_one(user_doc)
    user_doc["_id"] = result.inserted_id
    print("User created with ID:", result.inserted_id)

    return user_doc

def authenticate_user(email: str, password: str) -> Optional[dict]:
    user = get_user_by_email(email)
    

    if not user:
        return None

    if not verify_password(password, user["hashed_password"]):
        print("password not matched")
        return None

    if not user.get("is_active", False):
        return None
    
    print("authenticating",user)
    return user

def increment_user_stat(user_id: str, field: str, value: int = 1) -> None:
    users = get_users_collection()
    users.update_one(
        {"_id": ObjectId(user_id)},
        {"$inc": {f"stats.{field}": value}}
    )
