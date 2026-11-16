"""Agent 14: Returns & reverse logistics."""
from agents.base_agent import BaseAgent


class ReturnsAgent(BaseAgent):
    name = "ReturnsAgent"
    description = "Return rate & reverse logistics"

    def run(self):
        findings, metrics = [], {}
        ret_col = self._safe_col("returns", "return_qty", "returned")
        qty_col = self._safe_col("quantity", "qty", "units")

        if ret_col and self.can_run():
            try:
                total_ret = float(self.df[ret_col].sum())
                metrics["total_returns"] = total_ret
                if qty_col:
                    total_qty = float(self.df[qty_col].sum())
                    if total_qty > 0:
                        rate = total_ret / total_qty
                        metrics["return_rate"] = round(rate, 4)
                        if rate > 0.05:
                            findings.append(f"⚠ Return rate {rate*100:.2f}% (high)")
                        else:
                            findings.append(f"✓ Return rate {rate*100:.2f}%")
                else:
                    findings.append(f"Total returns: {total_ret:.0f}")
            except Exception:
                pass
        if not findings:
            findings.append("No returns data detected")
        return {"agent": self.name, "summary": "Returns analysis",
                "findings": findings, "metrics": metrics}
