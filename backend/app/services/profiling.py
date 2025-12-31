import pandas as pd
import numpy as np
from typing import Dict, Any

def profile_dataset(df: pd.DataFrame) -> Dict[str, Any]:
    profile = {
        "numeric": _profile_numeric(df),
        "categorical": _profile_categorical(df),
        "missing": _profile_missing(df)
    }
    return profile


def _profile_numeric(df: pd.DataFrame) -> Dict[str, Any]:
    numeric_cols = df.select_dtypes(include=["number"]).columns
    result = {}

    for col in numeric_cols:
        series = df[col].dropna()

        if series.empty:
            continue

        result[col] = {
            "mean": float(series.mean()),
            "min": float(series.min()),
            "max": float(series.max()),
            "std": float(series.std()),
            "trend": _detect_trend(series),
            "outliers": _detect_outliers(series)
        }

    return result


def _detect_trend(series: pd.Series) -> str:
    if len(series) < 3:
        return "flat"

    first_half = series.iloc[: len(series) // 2].mean()
    second_half = series.iloc[len(series) // 2 :].mean()

    if second_half > first_half * 1.05:
        return "up"
    elif second_half < first_half * 0.95:
        return "down"
    return "flat"


def _detect_outliers(series: pd.Series) -> list:
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1

    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    outliers = series[(series < lower) | (series > upper)]
    return outliers.head(5).tolist()


def _profile_categorical(df: pd.DataFrame) -> Dict[str, Any]:
    cat_cols = df.select_dtypes(include=["object", "category"]).columns
    result = {}

    for col in cat_cols:
        series = df[col].dropna()

        if series.empty:
            continue

        value_counts = series.value_counts().head(5)

        result[col] = {
            "unique_count": int(series.nunique()),
            "top_values": value_counts.to_dict()
        }

    return result


def _profile_missing(df: pd.DataFrame) -> Dict[str, Any]:
    result = {}

    for col in df.columns:
        missing_ratio = df[col].isna().mean()
        if missing_ratio > 0:
            result[col] = {
                "missing_ratio": float(missing_ratio)
            }

    return result
