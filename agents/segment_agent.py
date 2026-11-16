"""Agent 20: Product segmentation (ABC × XYZ)."""
import numpy as np
from agents.base_agent import BaseAgent


class SegmentAgent(BaseAgent):
    name = "SegmentAgent"
    description = "ABC × XYZ product segmentation"

    def run(self):
        findings, metrics = [], {}
        sku_col = self._safe_col("sku", "product_id", "item")
        qty_col = self._safe_col("quantity", "qty", "demand")
        price_col = self._safe_col("price", "unit_price", "cost")

        if sku_col and qty_col and self.can_run():
            try:
                df = self.df.copy()
                value = df[qty_col] * (df[price_col] if price_col else 1)
                agg = df.assign(_value=value).groupby(sku_col).agg(
                    total=("_value", "sum"), sd=(qty_col, "std"), mean=(qty_col, "mean")
                ).fillna(0)

                agg["cv"] = (agg["sd"] / agg["mean"].replace(0, np.nan)).fillna(0)
                agg["cum_pct"] = agg["total"].sort_values(ascending=False).cumsum() / max(agg["total"].sum(), 1)
                agg["abc"] = np.where(agg["cum_pct"] <= 0.8, "A",
                                     np.where(agg["cum_pct"] <= 0.95, "B", "C"))
                agg["xyz"] = np.where(agg["cv"] < 0.25, "X",
                                     np.where(agg["cv"] < 0.5, "Y", "Z"))
                agg["segment"] = agg["abc"] + agg["xyz"]
                seg = agg["segment"].value_counts().to_dict()
                metrics["segment_counts"] = seg
                findings.append("Segments: " + ", ".join(f"{k}={v}" for k, v in seg.items()))
                if seg.get("AZ", 0) > 0:
                    findings.append(f"⚠ {seg['AZ']} AZ items — high value + high volatility")
            except Exception as e:
                findings.append(f"Segmentation error: {e}")
        if not findings:
            findings.append("No SKU/quantity columns detected")
        return {"agent": self.name, "summary": "Segmentation",
                "findings": findings, "metrics": metrics}
