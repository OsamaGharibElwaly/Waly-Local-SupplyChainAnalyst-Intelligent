"""Agent 3: Supplier scoring & risk."""
from agents.base_agent import BaseAgent
from config import THRESHOLDS


class SupplierAgent(BaseAgent):
    name = "SupplierAgent"
    description = "Supplier performance and risk"

    def run(self):
        findings, metrics = [], {}
        sup_col = self._safe_col("supplier", "vendor", "supplier_name")
        score_col = self._safe_col("supplier_score", "score", "rating")

        if sup_col and self.can_run():
            metrics["supplier_count"] = int(self.df[sup_col].nunique())
            findings.append(f"{metrics['supplier_count']} unique suppliers")
            if score_col:
                avg = self.df[score_col].mean()
                metrics["avg_supplier_score"] = round(float(avg), 2)
                weak = self.df[self.df[score_col] < THRESHOLDS["supplier_score_warn"]]
                metrics["weak_suppliers"] = int(len(weak))
                if len(weak) > 0:
                    names = weak[sup_col].astype(str).unique()[:5].tolist()
                    findings.append(f"WARNING: {len(weak)} weak suppliers: {', '.join(names)}")
                else:
                    findings.append("All suppliers within tolerance")
        if not findings:
            findings.append("No supplier columns detected")
        return {"agent": self.name, "summary": "Supplier analysis",
                "findings": findings, "metrics": metrics}
