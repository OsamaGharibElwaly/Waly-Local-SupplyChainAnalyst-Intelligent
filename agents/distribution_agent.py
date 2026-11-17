"""Agent 24: Numeric distribution health across all numeric columns."""
import numpy as np
from agents.base_agent import BaseAgent
from tools.statistics_tools import distribution_stats


class DistributionAgent(BaseAgent):
    name = "DistributionAgent"
    description = "Distribution shape diagnostics for every numeric column"

    def run(self):
        findings, metrics = [], {}
        if not self.can_run():
            return {"agent": self.name, "summary": "Distribution",
                    "findings": ["No data"], "metrics": {}}
        num_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        if not num_cols:
            return {"agent": self.name, "summary": "Distribution",
                    "findings": ["No numeric columns"], "metrics": {}}

        skewed, normal, bimodal_like = [], [], []
        for col in num_cols:
            st = distribution_stats(self.df[col])
            if not st:
                continue
            skew = st.get("skew", 0)
            kurt = st.get("kurtosis", 0)
            if abs(skew) > 1.5:
                skewed.append(col)
            else:
                normal.append(col)
            if kurt > 5:
                bimodal_like.append(col)
            metrics[str(col) + "_skew"] = skew
            metrics[str(col) + "_kurt"] = kurt

        findings.append(
            "Numeric columns: " + str(len(num_cols)) + " total, " +
            str(len(skewed)) + " heavily skewed, " +
            str(len(normal)) + " near-normal"
        )
        if skewed:
            findings.append("Skewed: " + ", ".join(map(str, skewed[:8])))
        if bimodal_like:
            findings.append(
                "High kurtosis (possible outliers/fat tails): " + ", ".join(map(str, bimodal_like[:5]))
            )
        metrics["skewed_count"] = len(skewed)
        metrics["normal_count"] = len(normal)
        return {"agent": self.name, "summary": "Distribution diagnostics",
                "findings": findings, "metrics": metrics}
