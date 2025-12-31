import pandas as pd
from typing import Dict, Any


def infer_schema(df: pd.DataFrame) -> Dict[str, Any]:
    schema = {}

    for col in df.columns:
        series = df[col]

        schema[col] = {
            "type": _infer_type(series),
            "nullable": bool(series.isna().any()),
            "cardinality": _infer_cardinality(series)
        }

    return schema


def _infer_type(series: pd.Series) -> str:
    if pd.api.types.is_bool_dtype(series):
        return "boolean"

    if pd.api.types.is_numeric_dtype(series):
        return "numeric"

    if pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"

    # Try datetime coercion
    try:
        parsed = pd.to_datetime(series.dropna().head(20), errors="coerce")

        if parsed.notna().sum() >= 5:
            return "datetime"
    except Exception:
        pass

    unique_ratio = series.nunique() / max(len(series), 1)

    if unique_ratio < 0.2:
        return "categorical"

    return "text"
 

def _infer_cardinality(series: pd.Series) -> str:
    unique_ratio = series.nunique() / max(len(series), 1)

    if unique_ratio > 0.5:
        return "high"
    return "low"
