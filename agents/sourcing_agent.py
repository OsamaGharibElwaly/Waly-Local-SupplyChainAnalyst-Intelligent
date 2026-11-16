"""Agent 12: Sourcing — supplier concentration & diversification."""
from agents.base_agent import BaseAgent


class SourcingAgent(BaseAgent):
    name = "SourcingAgent"
    description = "Supplier concentration (HHI) & single-source risk"

    def run(self):
        findings, metrics = [], {}
        sup_col = self._safe_col("supplier", "vendor")
        qty_col = self._safe_col("quantity", "qty", "units")

        if sup_col and self.can_run():
            counts = self.df[sup_col].value_counts(normalize=True)
            hhi = float((counts ** 2).sum())  # 0 = diversified, 1 = monopoly
            metrics["hhi"] = round(hhi, 3)
            metrics["supplier_count"] = int(len(counts))
            if hhi > 0.5:
                findings.append(f"⚠ High concentration HHI={hhi:.2f} — single-source risk")
            elif hhi > 0.25:
                findings.append(f"Moderate concentration HHI={hhi:.2f}")
            else:
                findings.append(f"✓ Diversified sourcing HHI={hhi:.2f}")

            if qty_col:
                try:
                    top_sup = self.df.groupby(sup_col)[qty_col].sum().idxmax()
                    share = (self.df.groupby(sup_col)[qty_col].sum().max()
                             / self.df.groupby(sup_col)[qty_col].sum().sum())
                    metrics["top_supplier_share"] = round(float(share), 3)
                    findings.append(f"Top supplier '{top_sup}' = {share*100:.1f}% of volume")
                except Exception:
                    pass
        if not findings:
            findings.append("No sourcing data detected")
        return {"agent": self.name, "summary": "Sourcing analysis",
                "findings": findings, "metrics": metrics}
