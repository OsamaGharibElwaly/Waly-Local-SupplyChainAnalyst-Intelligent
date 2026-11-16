"""Chart data builders (aggregations only — rendering in frontend)."""
import pandas as pd


def bar_data(df, col, agg="sum", value=None, top=10):
    if col not in df.columns:
        return None
    if value and value in df.columns:
        s = df.groupby(col)[value].agg(agg).sort_values(ascending=False).head(top)
    else:
        s = df[col].value_counts().head(top)
    return {"labels": [str(i) for i in s.index.tolist()],
            "values": [float(v) for v in s.values.tolist()]}


def line_data(df, date_col, value_col, agg="sum"):
    try:
        d = df.copy()
        d[date_col] = pd.to_datetime(d[date_col], errors="coerce")
        d = d.dropna(subset=[date_col])
        s = getattr(d.groupby(date_col)[value_col], agg)().sort_index()
        return {"labels": [str(i.date()) for i in s.index],
                "values": [float(v) for v in s.values]}
    except Exception:
        return None


def histogram_data(series, bins=10):
    import numpy as np
    s = pd.to_numeric(series, errors="coerce").dropna()
    if s.empty:
        return None
    counts, edges = np.histogram(s, bins=bins)
    labels = [f"{edges[i]:.1f}–{edges[i+1]:.1f}" for i in range(len(counts))]
    return {"labels": labels, "values": [int(c) for c in counts]}
