from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
import json

from app.models.insights import InsightResponse
from app.core.config import settings
from app.services.insight_service import generate_insights
from app.core.dependencies import get_current_user

from bson import ObjectId
from datetime import datetime

from app.core.database import get_insights_collection


router = APIRouter(prefix="/insights", tags=["Insights"])

from fastapi import Query

@router.post("/generate", response_model=InsightResponse)
async def generate_dataset_insights(dataset_id: str = Query(..., description="Dataset ID to generate insights for"),current_user: dict = Depends(get_current_user),):
    dataset_dir = os.path.join(settings.DATASET_DIR, dataset_id)

    if not os.path.exists(dataset_dir):
        raise HTTPException(status_code=404, detail="Dataset not found")

    insights = generate_insights(dataset_id)

    insight_path = os.path.join(dataset_dir, "insights.json")

    with open(insight_path, "w") as f:
        json.dump(insights, f, indent=2)

    insights_col = get_insights_collection()

    insights_col.insert_one({
        "dataset_id": dataset_id,
        "user_id": str(current_user["_id"]),
        "generated_at": datetime.utcnow(),
        "has_summary": bool(insights.get("summary")),
        "path": insight_path,
    })


    return insights


@router.get("/{dataset_id}", response_model=InsightResponse)
async def get_dataset_insights(dataset_id: str,current_user: dict = Depends(get_current_user),):
    insights_col = get_insights_collection()

    insight_meta = insights_col.find_one({
        "dataset_id": dataset_id,
        "user_id": str(current_user["_id"]),
    })

    if not insight_meta:
        raise HTTPException(
            status_code=404,
            detail="Insights not generated yet"
        )

    with open(insight_meta["path"]) as f:
        return json.load(f)

