"""Agent 17: Capacity vs demand gap."""
from agents.base_agent import BaseAgent


class CapacityAgent(BaseAgent):
    name = "CapacityAgent"
    description = "Capacity gap & utilization trend"

    def run(self):
        findings, metrics = [], {}
        cap_col = self._safe_col("capacity", "max_capacity", "production_capacity")
        dem_col = self._safe_col("quantity", "demand", "qty", "units_sold")

        if cap_col and dem_col and self.can_run():
            try:
                cap_sum = float(self.df[cap_col].sum())
                dem_sum = float(self.df[dem_col].sum())
                if cap_sum > 0:
                    util = dem_sum / cap_sum
                    metrics["utilization"] = round(util, 3)
                    metrics["capacity_gap"] = round(cap_sum - dem_sum, 2)
                    if util > 0.95:
                        findings.append(f"⚠ Demand {util*100:.1f}% of capacity — overload risk")
                    elif util < 0.5:
                        findings.append(f"Underutilized ({util*100:.1f}% of capacity)")
                    else:
                        findings.append(f"✓ Healthy utilization {util*100:.1f}%")
            except Exception:
                pass
        if not findings:
            findings.append("No capacity/demand columns detected")
        return {"agent": self.name, "summary": "Capacity analysis",
                "findings": findings, "metrics": metrics}
