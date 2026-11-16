"""Agent 5: Composite risk scoring using knowledge rules."""
from agents.base_agent import BaseAgent


class RiskAgent(BaseAgent):
    name = "RiskAgent"
    description = "Composite supply chain risk scoring"

    def run(self):
        findings, metrics = [], {"risk_score": 0.0}
        score = 0.0
        df = self.df

        try:
            if self._safe_col("days_of_stock") and (df[self._safe_col("days_of_stock")] < 15).any():
                score += 0.9; findings.append("REORDER: stock below 15 days")
            if self._safe_col("lead_time_days") and (df[self._safe_col("lead_time_days")] > 30).any():
                score += 0.7; findings.append("HIGH_LEAD_TIME: > 30 days")
            if self._safe_col("defect_rate") and (df[self._safe_col("defect_rate")] > 0.03).any():
                score += 0.85; findings.append("QUALITY_ISSUE: defect rate > 3%")
            if self._safe_col("supplier_score") and (df[self._safe_col("supplier_score")] < 60).any():
                score += 0.8; findings.append("SUPPLIER_RISK: score < 60")
            otd = self._safe_col("on_time_delivery")
            if otd:
                r = df[otd].mean()
                r = r / 100 if r > 1 else r
                if r < 0.9:
                    score += 0.7; findings.append("DELIVERY_RISK: OTD < 90%")
        except Exception:
            pass

        metrics["risk_score"] = round(min(score / 3.95, 1.0) * 100, 1)
        if not findings:
            findings.append("No critical risk triggers")
        return {"agent": self.name, "summary": "Composite risk",
                "findings": findings, "metrics": metrics}
