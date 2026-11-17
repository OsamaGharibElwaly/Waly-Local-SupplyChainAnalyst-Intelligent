"""Advanced statistical helpers: correlation, regression, distribution diagnostics."""
import numpy as np
import pandas as pd


def correlation_matrix(df, method="pearson"):
    num = df.select_dtypes(include=[np.number])
    if num.shape[1] < 2:
        return None
    return num.corr(method=method).round(3)


def top_correlations(df, threshold=0.7, method="pearson"):
    corr = correlation_matrix(df, method)
    if corr is None:
        return []
    pairs = []
    cols = corr.columns
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            r = corr.iloc[i, j]
            if pd.notna(r) and abs(r) >= threshold:
                pairs.append((str(cols[i]), str(cols[j]), round(float(r), 3)))
    return sorted(pairs, key=lambda x: abs(x[2]), reverse=True)


def linear_trend(series):
    s = pd.Series(series).dropna()
    if len(s) < 3:
        return None
    x = np.arange(len(s), dtype=float)
    y = s.values.astype(float)
    try:
        slope, intercept = np.polyfit(x, y, 1)
        pred = slope * x + intercept
        ss_res = float(((y - pred) ** 2).sum())
        ss_tot = float(((y - y.mean()) ** 2).sum())
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0
        return {
            "slope": round(float(slope), 4),
            "intercept": round(float(intercept), 4),
            "r2": round(float(r2), 4),
            "direction": "up" if slope > 0 else "down" if slope < 0 else "flat",
        }
    except Exception:
        return None


def distribution_stats(series):
    s = pd.Series(series).dropna()
    if len(s) < 4:
        return {}
    return {
        "mean": round(float(s.mean()), 3),
        "median": round(float(s.median()), 3),
        "std": round(float(s.std()), 3),
        "skew": round(float(s.skew()), 3),
        "kurtosis": round(float(s.kurtosis()), 3),
        "q1": round(float(s.quantile(0.25)), 3),
        "q3": round(float(s.quantile(0.75)), 3),
        "min": round(float(s.min()), 3),
        "max": round(float(s.max()), 3),
    }


def zscore_outliers(series, threshold=2.5):
    s = pd.Series(series).dropna()
    if len(s) < 5 or s.std() == 0:
        return []
    z = (s - s.mean()) / s.std()
    return s.index[z.abs() > threshold].tolist()
