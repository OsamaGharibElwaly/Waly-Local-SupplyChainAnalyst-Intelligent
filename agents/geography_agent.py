"""Agent 16: Geographic distribution & regional risk."""
from agents.base_agent import BaseAgent


class GeographyAgent(BaseAgent):
    name = "GeographyAgent"
    description = "Regional distribution & concentration"

    def run(self):
        findings, metrics = [], {}
        geo_col = self._safe_col("country", "region", "location", "warehouse")

        if geo_col and self.can_run():
            counts = self.df[geo_col].value_counts()
            metrics["regions"] = int(len(counts))
            metrics["top_region"] = str(counts.idxmax())
            metrics["top_share"] = round(float(counts.iloc[0] / len(self.df)), 3)
            findings.append(f"{len(counts)} regions — top: {counts.idxmax()}")
            if metrics["top_share"] > 0.6:
                findings.append(f"⚠ Geographic concentration {metrics['top_share']*100:.1f}%")
            else:
                findings.append(f"✓ Balanced regional spread")
        if not findings:
            findings.append("No geography column detected")
        return {"agent": self.name, "summary": "Geography analysis",
                "findings": findings, "metrics": metrics}
