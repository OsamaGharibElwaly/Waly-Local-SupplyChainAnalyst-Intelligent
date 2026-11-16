"""Agent 11: Warehouse utilization & stock coverage."""
from agents.base_agent import BaseAgent
from tools.stats_tools import describe


class WarehouseAgent(BaseAgent):
    name = "WarehouseAgent"
    description = "Warehouse capacity & stock coverage"

    def run(self):
        findings, metrics = [], {}
        wh_col = self._safe_col("warehouse", "location", "site")
        stock_col = self._safe_col("stock", "inventory", "on_hand")
        cap_col = self._safe_col("capacity", "max_capacity")

        if wh_col and self.can_run():
            metrics["warehouses"] = int(self.df[wh_col].nunique())
            findings.append(f"{metrics['warehouses']} warehouse(s) detected")
            if stock_col:
                by_wh = self.df.groupby(wh_col)[stock_col].sum()
                top = by_wh.idxmax()
                metrics["busiest_warehouse"] = str(top)
                findings.append(f"Busiest: {top} ({float(by_wh.max()):.0f} units)")
            if cap_col and stock_col:
                util = (self.df[stock_col] / self.df[cap_col]).replace([float("inf")], 0).mean()
                metrics["avg_utilization"] = round(float(util), 3)
                if util > 0.85:
                    findings.append(f"⚠ Avg utilization {util*100:.1f}% — near capacity")
                else:
                    findings.append(f"✓ Avg utilization {util*100:.1f}%")
        if not findings:
            findings.append("No warehouse data detected")
        return {"agent": self.name, "summary": "Warehouse analysis",
                "findings": findings, "metrics": metrics}
