"""Agent 23: Reorder point & safety stock (EOQ-aware)."""
from agents.base_agent import BaseAgent
from tools.finance_tools import reorder_point, safety_stock, eoq


class ReorderAgent(BaseAgent):
    name = "ReorderAgent"
    description = "Reorder point, safety stock, and EOQ calculation"

    def run(self):
        findings, metrics = [], {}
        if not self.can_run():
            return {"agent": self.name, "summary": "Reorder",
                    "findings": ["No data"], "metrics": {}}

        qty_col = self._safe_col("quantity", "qty", "demand", "units_sold")
        lt_col = self._safe_col("lead_time_days", "lead_time", "leadtime")
        cost_col = self._safe_col("cost", "unit_cost", "price")
        stock_col = self._safe_col("stock", "inventory", "on_hand")

        if qty_col and lt_col:
            try:
                avg_daily = float(self.df[qty_col].sum()) / max(len(self.df), 1)
                avg_lt = float(self.df[lt_col].mean())
                demand_std = float(self.df[qty_col].std())
                ss = safety_stock(1.65, demand_std, avg_lt)
                rop = reorder_point(avg_daily, avg_lt, ss or 0)
                metrics["avg_daily_demand"] = round(avg_daily, 2)
                metrics["avg_lead_time"] = round(avg_lt, 1)
                metrics["safety_stock_95"] = ss
                metrics["reorder_point"] = rop
                findings.append(
                    "ROP=" + str(rop) + " (safety stock=" + str(ss) + " @95%)"
                )
                if stock_col:
                    below = int((self.df[stock_col] < rop).sum()) if rop else 0
                    metrics["below_rop"] = below
                    if below > 0:
                        findings.append(
                            "WARNING: " + str(below) + " rows below reorder point"
                        )
            except Exception as e:
                findings.append("Reorder error: " + str(e))

        if qty_col and cost_col:
            try:
                annual = float(self.df[qty_col].sum())
                unit_cost = float(self.df[cost_col].mean())
                q = eoq(annual, order_cost=50.0, holding_cost_per_unit=max(unit_cost * 0.2, 0.01))
                if q:
                    metrics["eoq_units"] = q
                    findings.append("EOQ (assumed $50 order cost, 20% holding) = " + str(q) + " units")
            except Exception:
                pass

        if not findings:
            findings.append("Insufficient data for reorder analysis")
        return {"agent": self.name, "summary": "Reorder & safety stock",
                "findings": findings, "metrics": metrics}
