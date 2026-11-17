"""Forecasting helpers: moving average, exponential smoothing, linear forecast."""
import numpy as np
import pandas as pd


def moving_average(series, window=3):
    s = pd.Series(series).dropna()
    if len(s) < window:
        return None
    return round(float(s.rolling(window).mean().iloc[-1]), 3)


def exponential_smoothing(series, alpha=0.3):
    s = pd.Series(series).dropna().astype(float)
    if s.empty:
        return None
    result = s.iloc[0]
    for v in s.iloc[1:]:
        result = alpha * v + (1 - alpha) * result
    return round(float(result), 3)


def linear_forecast(series, periods_ahead=1):
    s = pd.Series(series).dropna().astype(float)
    if len(s) < 3:
        return None
    x = np.arange(len(s), dtype=float)
    try:
        slope, intercept = np.polyfit(x, s.values, 1)
        forecast = slope * (len(s) - 1 + periods_ahead) + intercept
        return round(float(forecast), 3)
    except Exception:
        return None


def naive_forecast(series):
    s = pd.Series(series).dropna()
    if s.empty:
        return None
    return round(float(s.iloc[-1]), 3)


def forecast_triplet(series):
    return {
        "moving_average_3": moving_average(series, 3),
        "exponential_smoothing": exponential_smoothing(series, 0.3),
        "linear": linear_forecast(series, 1),
        "naive": naive_forecast(series),
    }
