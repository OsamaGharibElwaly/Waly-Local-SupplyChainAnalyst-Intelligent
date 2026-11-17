"""Agent 21: Correlation & multicollinearity detection."""
from agents.base_agent import BaseAgent
from tools.statistics_tools import top_correlations


class CorrelationAgent(BaseAgent):
    name = "CorrelationAgent"
    description = "Detect strong correlations between numeric columns"

    def run(self):
        findings, metrics = [], {}
        if not self.can_run():
            return {"agent": self.name, "summary": "Correlation",
                    "findings": ["No data"], "metrics": {}}
        pairs = top_correlations(self.df, threshold=0.7)
        if not pairs:
            findings.append("No strong correlations (|r| >= 0.7) found")
        else:
            metrics["strong_pairs"] = len(pairs)
            metrics["top_pair"] = pairs[0][0] + " ~ " + pairs[0][1]
            metrics["top_r"] = pairs[0][2]
            findings.append(str(len(pairs)) + " strong correlation pair(s) found")
            for a, b, r in pairs[:5]:
                findings.append("  " + a + " ~ " + b + ": r=" + str(r))
            if any(abs(r) > 0.95 for _, _, r in pairs):
                findings.append("WARNING: Near-perfect correlation - possible duplicate/derived column")
        return {"agent": self.name, "summary": "Correlation analysis",
                "findings": findings, "metrics": metrics}
