"""Agent 2: Inventory health."""
from agents.base_agent import BaseAgent
from config import THRESHOLDS


class InventoryAgent(BaseAgent):
    name = "InventoryAgent"
    description = "Inventory levels, reorder point, ABC classification"

    def run(self):
        findings, metrics = [], {}
        stock_col = self._safe_col("stock", "inventory", "on_hand", "days_of_stock")
        sku_col = self._safe_col("sku", "product_id", "item")
        value_col = self._safe_col("value", "revenue", "total_value")

        if stock_col and self.can_run():
            low = self.df[self.df[stock_col] < THRESHOLDS["low_stock_days"]]
            metrics["low_stock_skus"] = int(len(low))
            findings.append(f"{len(low)} SKUs below safety threshold (<{THRESHOLDS['low_stock_days']})")
            if len(low) > 0 and sku_col:
                findings.append("At risk: " + ", ".join(low[sku_col].astype(str).head(5).tolist()))
            if value_col:
                try:
                    total = self.df[value_col].sum()
                    if sku_col and total > 0:
                        top = self.df.groupby(sku_col)[value_col].sum().sort_values(ascending=False)
                        cum = top.cumsum() / total
                        metrics["abc_A_count"] = int((cum <= 0.8).sum()) + 1
                except Exception:
                    pass
        if not findings:
            findings.append("No inventory columns detected")
        return {"agent": self.name, "summary": "Inventory health",
                "findings": findings, "metrics": metrics}
