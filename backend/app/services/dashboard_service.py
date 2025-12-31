import os
import json
from uuid import uuid4
from typing import Dict, Any, List

from app.core.config import settings
from app.services.kpi_engine import generate_kpis
from app.services.chart_recommender import recommend_charts

from app.core.cache import cached
from datetime import datetime
from app.core.database import get_dashboards_collection, get_datasets_collection
from app.services.user_service import increment_user_stat

import pandas as pd

def _build_chart_data(df, x: str, y: str, aggregation: str | None):
    if df.empty or x not in df.columns or y not in df.columns:
        return []

    clean_df = df[[x, y]].dropna()

    if clean_df.empty:
        return []

    # Scatter charts → raw data
    if aggregation is None:
        return clean_df.head(200).to_dict(orient="records")

    if aggregation == "mean":
        return (
            clean_df.groupby(x, as_index=False)[y]
            .mean()
            .to_dict(orient="records")
        )

    if aggregation == "sum":
        return (
            clean_df.groupby(x, as_index=False)[y]
            .sum()
            .to_dict(orient="records")
        )

    return clean_df.head(200).to_dict(orient="records")

def _load_dataframe(dataset_dir: str) -> pd.DataFrame:
    for file in os.listdir(dataset_dir):
        if file.endswith(".csv"):
            return pd.read_csv(os.path.join(dataset_dir, file))
    return pd.DataFrame()


@cached
def generate_dashboard(dataset_id: str) -> Dict[str, Any]:
    dataset_dir = os.path.join(settings.DATASET_DIR, dataset_id)

    schema = _load_json(dataset_dir, "schema.json")
    profile = _load_json(dataset_dir, "profile.json")

    dashboard = {
        "dashboard_id": str(uuid4()),
        "dataset_id": dataset_id,
        "title": "Auto Generated Dashboard",
        "widgets": []
    }

    # KPIs
    dashboard["widgets"].extend([
        {
            "widget_id": str(uuid4()),
            "type": "kpi",
            **kpi
        }
        for kpi in generate_kpis(profile)
    ])

    # Charts
    df = _load_dataframe(dataset_dir)
    charts = recommend_charts(schema, profile)

    dashboard["widgets"].extend([
        {
            "widget_id": str(uuid4()),
            "type": "chart",
            "chart_type": chart["chart_type"],
            "x": chart["x"],
            "y": chart["y"],
            "aggregation": chart.get("aggregation"),
            "data": _build_chart_data(
                df,
                chart["x"],
                chart["y"],
                chart.get("aggregation")
            ) or []
        }
        for chart in charts
    ])

    # 🔒 Ensure dashboards directory exists
    os.makedirs(settings.DASHBOARD_DIR, exist_ok=True)

    # 📄 Write dashboard JSON to disk
    dashboard_path = os.path.join(
        settings.DASHBOARD_DIR,
        f"{dashboard['dashboard_id']}.json"
    )

    with open(dashboard_path, "w", encoding="utf-8") as f:
        json.dump(dashboard, f, indent=2, default=str)

    # 🗄️ Persist metadata to MongoDB
    dashboards_col = get_dashboards_collection()
    datasets_col = get_datasets_collection()

    dataset_doc = datasets_col.find_one({"dataset_id": dataset_id})

    if dataset_doc:
        dashboards_col.update_one(
            {
                "dataset_id": dataset_id,
                "user_id": dataset_doc["user_id"]
            },
            {
                "$set": {
                    "dashboard_id": dashboard["dashboard_id"],
                    "dataset_id": dataset_id,
                    "user_id": dataset_doc["user_id"],
                    "created_at": datetime.utcnow(),
                    "path": dashboard_path
                }
            },
            upsert=True
        )

        increment_user_stat(dataset_doc["user_id"], "dashboards_created")
    return dashboard

def _load_json(dataset_dir: str, filename: str) -> Dict[str, Any]:
    path = os.path.join(dataset_dir, filename)
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return json.load(f)

def _generate_kpis(profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    widgets = []

    for col, stats in profile.get("numeric", {}).items():
        widgets.append({
            "widget_id": str(uuid4()),
            "type": "kpi",
            "metric": f"{col}_mean",
            "value": round(stats.get("mean", 0), 2)
        })

    return widgets

def _generate_charts(schema: Dict[str, Any]) -> List[Dict[str, Any]]:
    widgets = []

    datetime_cols = [
        col for col, meta in schema.items()
        if meta["type"] == "datetime"
    ]

    numeric_cols = [
        col for col, meta in schema.items()
        if meta["type"] == "numeric"
    ]

    categorical_cols = [
        col for col, meta in schema.items()
        if meta["type"] == "categorical"
    ]

    # Time series charts
    for dt_col in datetime_cols:
        for num_col in numeric_cols:
            widgets.append({
                "widget_id": str(uuid4()),
                "type": "chart",
                "chart_type": "line",
                "x": dt_col,
                "y": num_col
            })

    # Categorical bar charts
    for cat_col in categorical_cols:
        for num_col in numeric_cols:
            widgets.append({
                "widget_id": str(uuid4()),
                "type": "chart",
                "chart_type": "bar",
                "x": cat_col,
                "y": num_col
            })

    return widgets
