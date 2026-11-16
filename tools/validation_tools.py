"""Data quality validation for imported CSVs."""
import pandas as pd

REQUIRED_HINTS = ["date", "sku", "supplier", "quantity", "cost"]

def validate(df):
    issues = []
    if df is None or df.empty:
        return ["Dataset is empty"]

    if df.isnull().any().any():
        n = int(df.isnull().sum().sum())
        issues.append(f"{n} missing values")

    dups = int(df.duplicated().sum())
    if dups:
        issues.append(f"{dups} duplicate rows")

    cols_lower = [c.lower() for c in df.columns]
    for hint in REQUIRED_HINTS:
        if hint not in cols_lower:
            issues.append(f"Recommended column missing: '{hint}'")

    for col in df.columns:
        if df[col].dtype == object:
            try:
                pd.to_numeric(df[col], errors="raise")
            except Exception:
                pass

    return issues


def schema_report(df):
    rows = []
    for c in df.columns:
        s = df[c]
        rows.append({
            "column": c,
            "dtype": str(s.dtype),
            "non_null": int(s.notna().sum()),
            "nulls": int(s.isna().sum()),
            "unique": int(s.nunique()),
        })
    return rows
