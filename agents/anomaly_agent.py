"""Agent 10: Multivariate anomaly detection (IQR-based)."""
import numpy as np
from agents.base_agent import BaseAgent


class AnomalyAgent(BaseAgent):
    name = "AnomalyAgent"
    description = "Statistical anomaly detection across numeric columns"

    def run(self):
        findings, metrics = [], {}
        if not self.can_run():
            return {"agent": self.name, "summary": "Anomaly detection",
                    "findings": ["No data"], "metrics": {}}
        num_df = self.df.select_dtypes(include=[np.number])
        if num_df.empty:
            return {"agent": self.name, "summary": "Anomaly detection",
                    "findings": ["No numeric columns"], "metrics": {}}
        total_anom, per_col = 0, {}
        for col in num_df.columns:
            vals = num_df[col].dropna()
            if len(vals) < 5:
                continue
            q1, q3 = vals.quantile(0.25), vals.quantile(0.75)
            iqr = q3 - q1
            if iqr == 0:
                continue
            low, high = q1 - 1.5 * iqr, q3 + 1.5 * iqr
            n = int(((vals < low) | (vals > high)).sum())
            if n:
                per_col[str(col)] = n
                total_anom += n
        metrics["total_anomalies"] = total_anom
        metrics["per_column"] = per_col
        if total_anom:
            findings.append(f"{total_anom} anomalies across {len(per_col)} column(s)")
            for k, v in per_col.items():
                findings.append(f"  - {k}: {v} outliers")
        else:
            findings.append("No significant anomalies")
        return {"agent": self.name, "summary": "Anomaly detection",
                "findings": findings, "metrics": metrics}
