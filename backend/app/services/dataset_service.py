import pandas as pd
import os
import json
from datetime import datetime

from app.core.config import settings
from app.services.schema_inference import infer_schema
from app.services.profiling import profile_dataset

# 🔹 MongoDB collections
from app.core.database import (
    get_datasets_collection,
    get_users_collection,
)


def process_dataset(dataset_id: str, file_path: str) -> None:
    dataset_dir = os.path.join(settings.DATASET_DIR, dataset_id)

    datasets_col = get_datasets_collection()
    users_col = get_users_collection()

    try:
        df = _load_dataset(file_path)
        df.columns = _normalize_columns(df.columns)

        schema = infer_schema(df)
        profile = profile_dataset(df)

        _save_json(dataset_dir, "schema.json", schema)
        _save_json(dataset_dir, "profile.json", profile)

        # ✅ UPDATE DATASET STATUS → READY (MongoDB)
        dataset_doc = datasets_col.find_one_and_update(
            {"dataset_id": dataset_id},
            {
                "$set": {
                    "status": "READY",
                    "updated_at": datetime.utcnow(),
                }
            },
            return_document=True,
        )

        # ✅ INCREMENT USER STATS (only on success)
        if dataset_doc:
            users_col.update_one(
                {"_id": dataset_doc["user_id"]},
                {"$inc": {"stats.datasets_uploaded": 1}},
            )

        # (Optional) keep metadata.json for debugging
        _update_metadata(dataset_dir, dataset_id, file_path, status="READY")

    except Exception as exc:
        # ❌ UPDATE DATASET STATUS → FAILED (MongoDB)
        datasets_col.update_one(
            {"dataset_id": dataset_id},
            {
                "$set": {
                    "status": "FAILED",
                    "updated_at": datetime.utcnow(),
                    "error": str(exc),
                }
            },
        )

        _update_metadata(dataset_dir, dataset_id, file_path, status="FAILED")
        raise exc

def _load_dataset(file_path: str) -> pd.DataFrame:
    if file_path.endswith(".csv"):
        return pd.read_csv(file_path)

    if file_path.endswith(".xlsx"):
        return pd.read_excel(file_path)

    if file_path.endswith(".json"):
        return pd.read_json(file_path)

    raise ValueError("Unsupported file format")

def _normalize_columns(columns):
    return [
        col.strip().lower().replace(" ", "_")
        for col in columns
    ]

def _update_metadata(
    dataset_dir: str,
    dataset_id: str,
    file_path: str,
    status: str
):
    metadata = {
        "dataset_id": dataset_id,
        "filename": os.path.basename(file_path),
        "status": status
    }

    _save_json(dataset_dir, "metadata.json", metadata)

def _save_json(dataset_dir: str, filename: str, data):
    path = os.path.join(dataset_dir, filename)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
