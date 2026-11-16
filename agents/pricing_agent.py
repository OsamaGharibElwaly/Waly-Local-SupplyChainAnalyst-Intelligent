"""Agent 13: Pricing & margin analysis."""
from agents.base_agent import BaseAgent


class PricingAgent(BaseAgent):
    name = "PricingAgent"
    description = "Price distribution & margin simulation"

    def run(self):
        findings, metrics = [], {}
        price_col = self._safe_col("price", "unit_price", "selling_price")
        cost_col = self._safe_col("cost", "unit_cost")
        qty_col = self._safe_col("quantity", "qty")

        if price_col and self.can_run():
            try:
                avg_p = float(self.df[price_col].mean())
                metrics["avg_price"] = round(avg_p, 2)
                findings.append(f"Avg price: {avg_p:.2f}")
                if cost_col:
                    avg_c = float(self.df[cost_col].mean())
                    metrics["avg_cost"] = round(avg_c, 2)
                    if avg_p > 0:
                        margin = (avg_p - avg_c) / avg_p
                        metrics["margin_pct"] = round(margin * 100, 2)
                        if margin < 0.1:
                            findings.append(f"⚠ Thin margin {margin*100:.1f}%")
                        elif margin > 0.4:
                            findings.append(f"✓ Healthy margin {margin*100:.1f}%")
                        else:
                            findings.append(f"Margin {margin*100:.1f}%")
            except Exception:
                pass
        if not findings:
            findings.append("No pricing data detected")
        return {"agent": self.name, "summary": "Pricing analysis",
                "findings": findings, "metrics": metrics}
