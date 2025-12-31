from datetime import datetime

import os
import json
from typing import List, Dict, Any

from app.core.config import settings
from app.services.llm_summarizer import summarize_insights
from app.services.kpi_engine import generate_kpis
from app.core.database import get_datasets_collection, get_insights_collection
from app.services.user_service import increment_user_stat


def _detect_trends(profile: Dict[str, Any]) -> List[Dict[str, str]]:
    insights = []

    for column, stats in profile.get("numeric", {}).items():
        trend = stats.get("trend")
        if trend == "up":
            insights.append({
                "type": "trend",
                "message": f"{column} shows an upward trend over time"
            })
        elif trend == "down":
            insights.append({
                "type": "trend",
                "message": f"{column} shows a downward trend over time"
            })

    return insights

def _detect_anomalies(profile: Dict[str, Any]) -> List[Dict[str, str]]:
    insights = []

    for column, stats in profile.get("numeric", {}).items():
        outliers = stats.get("outliers", [])
        if outliers:
            insights.append({
                "type": "anomaly",
                "message": f"{len(outliers)} anomalies detected in {column}"
            })

    return insights

def _data_quality_checks(
    profile: Dict[str, Any],
    schema: Dict[str, Any]
) -> List[Dict[str, str]]:
    insights = []

    for column, stats in profile.get("missing", {}).items():
        if stats["missing_ratio"] > 0.2:
            insights.append({
                "type": "data_quality",
                "message": f"Column '{column}' has {int(stats['missing_ratio'] * 100)}% missing values"
            })

    for column, meta in schema.items():
        if meta.get("cardinality") == "high":
            insights.append({
                "type": "data_distribution",
                "message": f"Column '{column}' has high cardinality"
            })

    return insights

def _kpi_based_insights(kpis: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    insights = []

    for kpi in kpis:
        if kpi["name"] == "row_count" and kpi["value"] < 100:
            insights.append({
                "type": "data_volume",
                "message": "Dataset has a relatively small number of records"
            })

        if kpi["name"].endswith("_max") and kpi["value"] is not None:
            insights.append({
                "type": "kpi",
                "message": f"{kpi['metric']} is {kpi['value']}"
            })

    return insights


def generate_insights(dataset_id: str) -> Dict[str, Any]:
    dataset_dir = os.path.join(settings.DATASET_DIR, dataset_id)

    profile = _load_json(dataset_dir, "profile.json")
    schema = _load_json(dataset_dir, "schema.json")

    insights: List[Dict[str, str]] = []

    insights.extend(_detect_trends(profile))
    insights.extend(_detect_anomalies(profile))
    insights.extend(_data_quality_checks(profile, schema))

    kpis = generate_kpis(profile)
    insights.extend(_kpi_based_insights(kpis))

    summary = summarize_insights(insights) if insights else None

    # ✅ MongoDB: persist insight metadata
    insights_col = get_insights_collection()
    datasets_col = get_datasets_collection()

    dataset_doc = datasets_col.find_one({"dataset_id": dataset_id})

    if dataset_doc:
        insights_col.update_one(
            {
                "dataset_id": dataset_id,
                "user_id": dataset_doc["user_id"]
            },
            {
                "$set": {
                    "dataset_id": dataset_id,
                    "user_id": dataset_doc["user_id"],
                    "generated_at": datetime.utcnow(),
                    "has_summary": bool(summary),
                    "path": os.path.join(dataset_dir, "insights.json")
                }
            },
            upsert=True
        )

        increment_user_stat(dataset_doc["user_id"], "insights_generated")

    return {
        "dataset_id": dataset_id,
        "insights": insights,
        "summary": summary
    }


def _load_json(dataset_dir: str, filename: str) -> Dict[str, Any]:
    path = os.path.join(dataset_dir, filename)
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return json.load(f)
