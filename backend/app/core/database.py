from typing import Optional
from pymongo import MongoClient
from pymongo.database import Database

from app.core.config import settings

_client: Optional[MongoClient] = None
_db: Optional[Database] = None

def get_users_collection():
    print("Getting users collection")
    return get_database()["users"]


def get_datasets_collection():
    return get_database()["datasets"]


def get_dashboards_collection():
    return get_database()["dashboards"]


def get_insights_collection():
    return get_database()["insights"]


def get_database() -> Database:
    global _client, _db

    if _db is not None:
        return _db

    if not settings.MONGODB_URI:
        raise RuntimeError("MONGODB_URI is not configured")

    _client = MongoClient(
        settings.MONGODB_URI,
        serverSelectionTimeoutMS=5000
    )

    _db = _client[settings.MONGODB_DB_NAME]
    return _db
