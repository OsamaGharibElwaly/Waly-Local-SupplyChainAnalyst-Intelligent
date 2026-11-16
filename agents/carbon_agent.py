"""Agent 18: Sustainability / carbon footprint estimate."""
from agents.base_agent import BaseAgent

# kg CO2 per unit shipped, by mode (very coarse illustrative factors)
MODE_FACTOR = {"air": 0.5, "truck": 0.12, "rail": 0.04, "sea": 0.015, "ocean": 0.015}


class CarbonAgent(BaseAgent):
    name = "CarbonAgent"
    description = "Estimated CO2 footprint & green opportunities"

    def run(self):
        findings, metrics = [], {}
        mode_col = self._safe_col("mode", "shipping_method", "carrier")
        qty_col = self._safe_col("quantity", "qty", "units", "weight")

        if mode_col and self.can_run():
            total_co2 = 0.0
            by_mode = {}
            df = self.df
            for mode, sub in df.groupby(mode_col):
                factor = MODE_FACTOR.get(str(mode).lower(), 0.1)
                vol = float(sub[qty_col].sum()) if qty_col else len(sub)
                co2 = vol * factor
                by_mode[str(mode)] = round(co2, 2)
                total_co2 += co2
            metrics["total_co2_kg"] = round(total_co2, 2)
            metrics["by_mode"] = by_mode
            findings.append(f"Estimated CO2 footprint: {total_co2:.1f} kg")
            if "air" in {m.lower() for m in by_mode}:
                findings.append("⚠ Air freight detected — consider sea/rail to reduce CO2")
        if not findings:
            findings.append("No shipping mode column detected")
        return {"agent": self.name, "summary": "Carbon footprint",
                "findings": findings, "metrics": metrics}
