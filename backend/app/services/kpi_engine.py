from typing import Dict, Any, List

def generate_kpis(profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    kpis = []

    kpis.extend(_row_count_kpi(profile))
    kpis.extend(_numeric_summary_kpis(profile))

    return kpis


def _row_count_kpi(profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    row_count = profile.get("row_count")

    if row_count is None:
        return []

    return [{
        "name": "row_count",
        "metric": "Total Records",
        "value": row_count,
        "format": "number"
    }]


def _numeric_summary_kpis(profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    kpis = []

    for col, stats in profile.get("numeric", {}).items():
        kpis.append({
            "name": f"{col}_mean",
            "metric": f"Average {col.replace('_', ' ').title()}",
            "value": round(stats.get("mean", 0), 2),
            "format": "number"
        })

        kpis.append({
            "name": f"{col}_max",
            "metric": f"Max {col.replace('_', ' ').title()}",
            "value": stats.get("max"),
            "format": "number"
        })

    return kpis
