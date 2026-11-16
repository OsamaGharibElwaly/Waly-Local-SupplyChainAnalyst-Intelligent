"""Agent 1: Demand forecasting with simple moving average + trend."""
import pandas as pd
from agents.base_agent import BaseAgent


class DemandForecastAgent(BaseAgent):
    name = "DemandForecastAgent"
    description = "Forecasts demand using moving average & trend detection"

    def run(self):
        qty_col = self._safe_col("quantity", "qty", "demand", "units_sold")
        date_col = self._safe_col("date", "order_date")
        findings, metrics = [], {}

        if qty_col and date_col and self.can_run():
            df = self.df.copy()
            df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
            df = df.dropna(subset=[date_col])
            ts = df.groupby(date_col)[qty_col].sum().sort_index()
            if len(ts) >= 3:
                ma3 = ts.rolling(3).mean().iloc[-1]
                last = ts.iloc[-1]
                trend = "up" if last > ts.mean() else "down"
                metrics.update({
                    "next_period_forecast": round(float(ma3), 2),
                    "last_value": float(last),
                    "mean": round(float(ts.mean()), 2),
                    "trend": trend,
                })
                findings.append(f"3-period forecast: {ma3:.2f} ({trend})")
                findings.append("Upward demand trend" if trend == "up" else "Downward demand trend")
        if not findings:
            findings.append("Insufficient data for demand forecast")
        return {"agent": self.name, "summary": "Demand forecast",
                "findings": findings, "metrics": metrics}
