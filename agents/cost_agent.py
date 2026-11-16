"""Agent 7: Cost analysis & anomaly detection."""
from agents.base_agent import BaseAgent


class CostAgent(BaseAgent):
    name = "CostAgent"
    description = "Cost analysis & anomaly detection"

    def run(self):
        findings, metrics = [], {}
        cost_col = self._safe_col("cost", "unit_cost", "total_cost", "price")
        if cost_col and self.can_run() and len(self.df) > 3:
            try:
                vals = self.df[cost_col].dropna()
                mean, std = float(vals.mean()), float(vals.std())
                metrics["avg_cost"] = round(mean, 2)
                metrics["std_cost"] = round(std, 2)
                findings.append(f"Avg cost: {mean:.2f} (sd={std:.2f})")
                if std > 0:
                    z = (vals - mean) / std
                    outliers = int((z.abs() > 2.5).sum())
                    metrics["cost_outliers"] = outliers
                    findings.append(f"{outliers} cost outliers (|z|>2.5)")
            except Exception as e:
                findings.append(f"Cost analysis error: {e}")
        if not findings:
            findings.append("No cost column detected")
        return {"agent": self.name, "summary": "Cost analysis",
                "findings": findings, "metrics": metrics}
