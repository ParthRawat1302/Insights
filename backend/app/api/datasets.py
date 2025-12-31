from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel
from uuid import uuid4
from typing import List
import os
import shutil
from app.models.dataset import DatasetResponse, DatasetListResponse

from app.services.dataset_service import process_dataset
from app.core.config import settings
from app.core.dependencies import get_current_user

from bson import ObjectId
from datetime import datetime

from app.core.database import get_datasets_collection


router = APIRouter(prefix="/datasets", tags=["Datasets"])


@router.post("/upload", response_model=DatasetResponse)
async def upload_dataset(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    if file.content_type not in settings.ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type"
        )

    dataset_id = str(uuid4())
    upload_dir = os.path.join(settings.DATASET_DIR, dataset_id)
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, file.filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception:
        raise HTTPException(status_code=500, detail="File upload failed")

    datasets_col = get_datasets_collection()

    datasets_col.insert_one({
        "dataset_id": dataset_id,
        "user_id": str(current_user["_id"]),
        "filename": file.filename,
        "status": "PROCESSING",
        "created_at": datetime.utcnow(),
        "path": file_path,
    })


    background_tasks.add_task(process_dataset, dataset_id, file_path)

    return DatasetResponse(
        dataset_id=dataset_id,
        filename=file.filename,
        status="PROCESSING"
    )


@router.get("/{dataset_id}", response_model=DatasetResponse)
async def get_dataset(dataset_id: str,current_user: dict = Depends(get_current_user),):
    datasets_col = get_datasets_collection()

    dataset = datasets_col.find_one({
        "dataset_id": dataset_id,
        "user_id": str(current_user["_id"]),
    })

    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    return DatasetResponse(
        dataset_id=dataset["dataset_id"],
        filename=dataset["filename"],
        status=dataset["status"],
    )



@router.get("/", response_model=List[DatasetListResponse])
async def list_datasets(current_user: dict = Depends(get_current_user)):
    datasets_col = get_datasets_collection()

    datasets = datasets_col.find({
        "user_id": str(current_user["_id"])
    })

    return [
        DatasetListResponse(
            dataset_id=d["dataset_id"],
            filename=d["filename"],
            status=d["status"],
        )
        for d in datasets
    ]

