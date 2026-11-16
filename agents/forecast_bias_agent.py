"""Agent 19: Forecast bias (actual vs forecast)."""
from agents.base_agent import BaseAgent


class ForecastBiasAgent(BaseAgent):
    name = "ForecastBiasAgent"
    description = "Forecast accuracy (MAPE) & bias"

    def run(self):
        findings, metrics = [], {}
        fc_col = self._safe_col("forecast", "forecast_qty", "planned")
        ac_col = self._safe_col("actual", "quantity", "qty", "demand")

        if fc_col and ac_col and self.can_run():
            try:
                df = self.df.dropna(subset=[fc_col, ac_col])
                if len(df) > 0:
                    err = df[ac_col] - df[fc_col]
                    bias = float(err.mean())
                    mape = float((err.abs() / df[ac_col].replace(0, 1)).mean() * 100)
                    metrics["bias"] = round(bias, 2)
                    metrics["mape_pct"] = round(mape, 2)
                    if bias > 0:
                        findings.append(f"Forecast under-predicts by {bias:.1f} on average")
                    elif bias < 0:
                        findings.append(f"Forecast over-predicts by {abs(bias):.1f}")
                    else:
                        findings.append("✓ No forecast bias")
                    if mape > 25:
                        findings.append(f"⚠ MAPE {mape:.1f}% — low forecast accuracy")
                    else:
                        findings.append(f"✓ MAPE {mape:.1f}% within tolerance")
            except Exception:
                pass
        if not findings:
            findings.append("No forecast/actual columns detected")
        return {"agent": self.name, "summary": "Forecast bias",
                "findings": findings, "metrics": metrics}
