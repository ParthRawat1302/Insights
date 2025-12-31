import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Project paths
    BASE_DIR: Path = Path(__file__).resolve().parents[2]

    DATA_DIR: Path = BASE_DIR / "data"
    DATASET_DIR: Path = DATA_DIR / "datasets"
    DASHBOARD_DIR: Path = DATA_DIR / "dashboards"

    # File upload
    MAX_UPLOAD_SIZE_MB: int = 100
    ALLOWED_FILE_TYPES: list[str] = [
        "text/csv",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/json"
    ]

    # JWT configuration
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "change-me")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60


    # LLM configuration
    COHERE_API_KEY: str | None = os.getenv("COHERE_API_KEY")
    COHERE_MODEL: str = "c4ai-command"

    # MongoDB configuration
    MONGODB_URI: str | None = os.getenv("MONGODB_URI")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "smart_dashboard_db")


    # Environment
    ENV: str = os.getenv("ENV", "development")

    class Config:
        env_file = ".env"

settings = Settings()