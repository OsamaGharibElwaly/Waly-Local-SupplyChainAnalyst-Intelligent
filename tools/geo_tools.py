"""Geographic helpers: concentration, HHI, region grouping."""
import pandas as pd


def herfindahl_index(shares):
    total = sum(shares)
    if total <= 0:
        return None
    return round(sum((s / total) ** 2 for s in shares), 4)


def concentration_ratio(counts, top_n=3):
    total = sum(counts)
    if total <= 0:
        return None
    top = sorted(counts, reverse=True)[:top_n]
    return round(sum(top) / total, 4)


def regional_summary(df, region_col, value_col=None):
    if region_col not in df.columns:
        return None
    if value_col and value_col in df.columns:
        g = df.groupby(region_col)[value_col].agg(["sum", "count", "mean"]).round(3)
        return g.to_dict(orient="index")
    return df[region_col].value_counts().to_dict()
