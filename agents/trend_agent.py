"""Agent 22: Time-series trend & distribution shape."""
from agents.base_agent import BaseAgent
from tools.statistics_tools import linear_trend, distribution_stats
import pandas as pd


class TrendAgent(BaseAgent):
    name = "TrendAgent"
    description = "Linear trend detection & distribution diagnostics"

    def run(self):
        findings, metrics = [], {}
        if not self.can_run():
            return {"agent": self.name, "summary": "Trend",
                    "findings": ["No data"], "metrics": {}}

        date_col = self._safe_col("date", "order_date", "created_at")
        qty_col = self._safe_col("quantity", "qty", "demand", "units_sold", "value")

        if date_col and qty_col:
            try:
                df = self.df.copy()
                df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
                df = df.dropna(subset=[date_col])
                ts = df.groupby(date_col)[qty_col].sum().sort_index()
                trend = linear_trend(ts)
                if trend:
                    metrics["slope"] = trend["slope"]
                    metrics["r2"] = trend["r2"]
                    metrics["direction"] = trend["direction"]
                    findings.append(
                        "Trend " + trend["direction"] + " (slope=" + str(trend["slope"]) +
                        ", R2=" + str(trend["r2"]) + ")"
                    )
                    if trend["r2"] > 0.7:
                        findings.append("Strong linear trend")
                    elif trend["r2"] < 0.2:
                        findings.append("WARNING: Weak linear fit - consider non-linear analysis")
            except Exception as e:
                findings.append("Trend error: " + str(e))

        num_cols = self.df.select_dtypes(include="number").columns.tolist()
        for col in num_cols[:2]:
            stats = distribution_stats(self.df[col])
            if stats:
                if abs(stats.get("skew", 0)) > 1.5:
                    findings.append(
                        "'" + str(col) + "' heavily skewed (" + str(stats["skew"]) +
                        ") - consider log transform"
                    )
                metrics[str(col) + "_skew"] = stats.get("skew")
                metrics[str(col) + "_kurtosis"] = stats.get("kurtosis")

        if not findings:
            findings.append("Insufficient data for trend analysis")
        return {"agent": self.name, "summary": "Trend & distribution",
                "findings": findings, "metrics": metrics}
