"""Advanced statistical helpers reused across agents."""
import numpy as np
import pandas as pd


def describe(series):
    s = pd.to_numeric(series, errors="coerce").dropna()
    if s.empty:
        return {}
    return {
        "count": int(s.count()),
        "mean": round(float(s.mean()), 4),
        "median": round(float(s.median()), 4),
        "std": round(float(s.std() or 0), 4),
        "min": round(float(s.min()), 4),
        "max": round(float(s.max()), 4),
        "p90": round(float(s.quantile(0.9)), 4),
    }


def iqr_outliers(series, k=1.5):
    s = pd.to_numeric(series, errors="coerce").dropna()
    if len(s) < 5:
        return 0
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    iqr = q3 - q1
    if iqr == 0:
        return 0
    return int(((s < q1 - k * iqr) | (s > q3 + k * iqr)).sum())


def correlation(df, a, b):
    try:
        x = pd.to_numeric(df[a], errors="coerce")
        y = pd.to_numeric(df[b], errors="coerce")
        return round(float(x.corr(y)), 3)
    except Exception:
        return None


def cv(series):
    """Coefficient of variation (std/mean) — useful for volatility."""
    s = pd.to_numeric(series, errors="coerce").dropna()
    if s.empty or s.mean() == 0:
        return 0.0
    return round(float(s.std() / abs(s.mean())), 4)


def trend_slope(series):
    """Linear regression slope (per-step)."""
    s = pd.to_numeric(series, errors="coerce").dropna().reset_index(drop=True)
    if len(s) < 2:
        return 0.0
    x = np.arange(len(s))
    try:
        slope = np.polyfit(x, s.values, 1)[0]
        return round(float(slope), 4)
    except Exception:
        return 0.0
