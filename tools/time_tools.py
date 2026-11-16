"""Time-series utilities for agents."""
import pandas as pd


def parse_dates(series):
    return pd.to_datetime(series, errors="coerce")


def daily_series(df, date_col, value_col, agg="sum"):
    d = df.copy()
    d[date_col] = parse_dates(d[date_col])
    d = d.dropna(subset=[date_col])
    return getattr(d.groupby(d[date_col])[value_col], agg)().sort_index()


def moving_average(series, window=3):
    return series.rolling(window, min_periods=1).mean()


def period_over_period(series):
    if len(series) < 2:
        return 0.0
    last, prev = series.iloc[-1], series.iloc[-2]
    if prev == 0:
        return 0.0
    return round(float((last - prev) / abs(prev)), 3)


def seasonality_strength(series, period=7):
    """Simple ratio of same-phase variance to total variance."""
    if len(series) < period * 2:
        return 0.0
    import numpy as np
    vals = series.values
    phase_means = [vals[i::period].mean() for i in range(period)]
    if np.std(vals) == 0:
        return 0.0
    return round(float(np.std(phase_means) / np.std(vals)), 3)
