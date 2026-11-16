"""Agent 15: Compliance checks (rule-based)."""
from agents.base_agent import BaseAgent


class ComplianceAgent(BaseAgent):
    name = "ComplianceAgent"
    description = "Compliance & data quality gates"

    def run(self):
        findings, metrics = [], {}
        if not self.can_run():
            return {"agent": self.name, "summary": "Compliance",
                    "findings": ["No data"], "metrics": {}}
        checks = 0
        passed = 0

        # Check: no negative costs / quantities
        for c in self.df.columns:
            lc = str(c).lower()
            if any(k in lc for k in ("cost", "price", "quantity", "qty")):
                try:
                    neg = int((self.df[c] < 0).sum())
                    checks += 1
                    if neg == 0:
                        passed += 1
                    else:
                        findings.append(f"⚠ '{c}' has {neg} negative values")
                except Exception:
                    pass

        # Check: no missing critical columns
        for hint in ("date", "sku"):
            checks += 1
            if any(hint in str(c).lower() for c in self.df.columns):
                passed += 1
            else:
                findings.append(f"⚠ Missing column hint '{hint}'")

        metrics["checks"] = checks
        metrics["passed"] = passed
        metrics["compliance_pct"] = round(passed / checks * 100, 1) if checks else 0.0
        if passed == checks:
            findings.insert(0, f"✓ All {checks} compliance checks passed")
        return {"agent": self.name, "summary": "Compliance",
                "findings": findings or ["✓ No issues"], "metrics": metrics}
