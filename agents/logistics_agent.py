"""Agent 4: Logistics & delivery performance."""
from agents.base_agent import BaseAgent


class LogisticsAgent(BaseAgent):
    name = "LogisticsAgent"
    description = "Logistics and on-time delivery"

    def run(self):
        findings, metrics = [], {}
        otd_col = self._safe_col("on_time_delivery", "otd", "delivered_on_time")
        cost_col = self._safe_col("shipping_cost", "freight", "transport_cost")
        mode_col = self._safe_col("mode", "carrier", "shipping_method")

        if otd_col and self.can_run():
            try:
                rate = float(self.df[otd_col].mean())
                if rate > 1:
                    rate = rate / 100.0
                metrics["on_time_rate"] = round(rate, 3)
                findings.append(f"On-time delivery {rate*100:.1f}%")
            except Exception:
                pass
        if cost_col and self.can_run():
            try:
                metrics["avg_shipping_cost"] = round(float(self.df[cost_col].mean()), 2)
                findings.append(f"Avg shipping cost: {metrics['avg_shipping_cost']}")
            except Exception:
                pass
        if mode_col and self.can_run():
            try:
                modes = self.df[mode_col].value_counts().to_dict()
                metrics["shipping_modes"] = {str(k): int(v) for k, v in modes.items()}
            except Exception:
                pass
        if not findings:
            findings.append("No logistics data detected")
        return {"agent": self.name, "summary": "Logistics performance",
                "findings": findings, "metrics": metrics}
