"""Agent 8: Quality / defect analysis."""
from agents.base_agent import BaseAgent
from config import THRESHOLDS


class QualityAgent(BaseAgent):
    name = "QualityAgent"
    description = "Quality metrics & defect rate"

    def run(self):
        findings, metrics = [], {}
        defect_col = self._safe_col("defect_rate", "defects", "quality_score")
        if defect_col and self.can_run():
            try:
                avg = float(self.df[defect_col].mean())
                if avg > 1:
                    avg = avg / 100.0
                metrics["avg_defect_rate"] = round(avg, 4)
                if avg > THRESHOLDS["high_defect_rate"]:
                    findings.append(f"WARNING: Defect rate {avg*100:.2f}% exceeds 3%")
                else:
                    findings.append(f"Defect rate {avg*100:.2f}% within tolerance")
            except Exception:
                pass
        if not findings:
            findings.append("No quality column detected")
        return {"agent": self.name, "summary": "Quality analysis",
                "findings": findings, "metrics": metrics}
