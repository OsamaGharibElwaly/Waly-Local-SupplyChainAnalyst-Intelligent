"""Agent 9: Lead time analysis."""
from agents.base_agent import BaseAgent
from config import THRESHOLDS


class LeadTimeAgent(BaseAgent):
    name = "LeadTimeAgent"
    description = "Lead time performance & variability"

    def run(self):
        findings, metrics = [], {}
        lt_col = self._safe_col("lead_time_days", "lead_time", "leadtime")
        if lt_col and self.can_run():
            try:
                vals = self.df[lt_col].dropna()
                avg = float(vals.mean())
                mx = float(vals.max())
                mn = float(vals.min())
                metrics.update({
                    "avg_lead_time": round(avg, 1),
                    "max_lead_time": round(mx, 1),
                    "min_lead_time": round(mn, 1),
                    "std_lead_time": round(float(vals.std()), 2),
                })
                findings.append(f"Avg lead time: {avg:.1f} days (min {mn:.0f}, max {mx:.0f})")
                if avg > THRESHOLDS["high_lead_time"]:
                    findings.append(f"WARNING: avg exceeds {THRESHOLDS['high_lead_time']} days")
            except Exception:
                pass
        if not findings:
            findings.append("No lead time column detected")
        return {"agent": self.name, "summary": "Lead time analysis",
                "findings": findings, "metrics": metrics}
