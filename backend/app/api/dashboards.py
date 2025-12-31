from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from uuid import uuid4
import json
import os

from app.core.config import settings
from app.services.dashboard_service import generate_dashboard
from app.models.dashboard import DashboardResponse
from app.core.dependencies import get_current_user

from bson import ObjectId
from datetime import datetime

from app.core.database import get_dashboards_collection 


router = APIRouter(prefix="/dashboards", tags=["Dashboards"])
from app.models.dashboard import DashboardCreateResponse

@router.post("/", response_model=DashboardCreateResponse)
async def create_dashboard(dataset_id: str,current_user: dict = Depends(get_current_user),):
    dataset_path = os.path.join(settings.DATASET_DIR, dataset_id)

    if not os.path.exists(dataset_path):
        raise HTTPException(status_code=404, detail="Dataset not found")

    dashboard = generate_dashboard(dataset_id)

    dashboard_path = os.path.join(
        settings.DASHBOARD_DIR,
        f"{dashboard['dashboard_id']}.json"
    )

    with open(dashboard_path, "w") as f:
        json.dump(dashboard, f, indent=2,default=str)

    dashboards_col = get_dashboards_collection()
    dashboards_col.insert_one({
        "dashboard_id": dashboard["dashboard_id"],
        "dataset_id": dataset_id,
        "user_id": str(current_user["_id"]),
        "created_at": datetime.utcnow(),
        "path": dashboard_path,
    })


    return {"dashboard_id": dashboard["dashboard_id"]}

@router.get("/{dashboard_id}", response_model=DashboardResponse)
async def get_dashboard(dashboard_id: str,current_user: dict = Depends(get_current_user),):
    dashboards_col = get_dashboards_collection()

    dashboard_meta = dashboards_col.find_one({
        "dashboard_id": dashboard_id,
        "user_id": str(current_user["_id"]),
    })

    if not dashboard_meta:
        raise HTTPException(status_code=404, detail="Dashboard not found")

    with open(dashboard_meta["path"]) as f:
        return json.load(f)


@router.get("/by-dataset/{dataset_id}", response_model=DashboardResponse)
async def get_dashboard_by_dataset(dataset_id: str,current_user: dict = Depends(get_current_user),):
    dashboards_col = get_dashboards_collection()

    dashboard_meta = dashboards_col.find_one({
        "dataset_id": dataset_id,
        "user_id": str(current_user["_id"]),
    })

    if not dashboard_meta:
        # 🔥 AUTO-GENERATE
        dashboard = generate_dashboard(dataset_id)
        return dashboard

    if not dashboard_meta:
        raise HTTPException(
            status_code=404,
            detail="Dashboard not found for dataset"
        )

    with open(dashboard_meta["path"]) as f:
        return json.load(f)


