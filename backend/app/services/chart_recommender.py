from typing import Dict, Any, List

def recommend_charts(
    schema: Dict[str, Any],
    profile: Dict[str, Any]
) -> List[Dict[str, Any]]:
    charts: List[Dict[str, Any]] = []

    charts.extend(_time_series_charts(schema))
    charts.extend(_categorical_numeric_charts(schema))
    charts.extend(_numeric_scatter_charts(schema))

    return charts[:6]

def _time_series_charts(schema: Dict[str, Any]) -> List[Dict[str, Any]]:
    charts = []

    datetime_cols = [
        col for col, meta in schema.items()
        if meta["type"] == "datetime"
    ]

    numeric_cols = [
        col for col, meta in schema.items()
        if meta["type"] == "numeric"
    ]

    for dt in datetime_cols:
        for num in numeric_cols:
            charts.append({
                "type": "chart",
                "chart_type": "line",
                "x": dt,
                "y": num,
                "reason": "Time series numeric trend"
            })

    return charts

def _categorical_numeric_charts(schema: Dict[str, Any]) -> List[Dict[str, Any]]:
    charts = []

    categorical_cols = [
        col for col, meta in schema.items()
        if meta["type"] == "categorical"
    ]

    numeric_cols = [
        col for col, meta in schema.items()
        if meta["type"] == "numeric"
    ]

    for cat in categorical_cols:
        for num in numeric_cols:
           charts.append({
                "type": "chart",
                "chart_type": "bar",
                "x": cat,
                "y": num,
                "aggregation": "mean",
                "reason": "Category comparison"
            })


    return charts

def _numeric_scatter_charts(schema: Dict[str, Any]) -> List[Dict[str, Any]]:
    charts = []

    numeric_cols = [
        col for col, meta in schema.items()
        if meta["type"] == "numeric"
    ]

    for i in range(len(numeric_cols)):
        for j in range(i + 1, len(numeric_cols)):
            charts.append({
                "type": "chart",
                "chart_type": "scatter",
                "x": numeric_cols[i],
                "y": numeric_cols[j],
                "aggregation": None,
                "reason": "Correlation analysis"
            })


    return charts



