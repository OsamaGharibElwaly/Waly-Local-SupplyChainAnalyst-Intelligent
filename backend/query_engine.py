"""Simple rule-based query engine over agent results (powers the chat widget)."""
import re


class QueryEngine:
    """Answer natural-language-ish questions using already-computed agent results."""

    def __init__(self):
        self.results = []

    def set_results(self, results):
        self.results = results or []

    def _find(self, name):
        return next((r for r in self.results if r.get("agent") == name), None)

    def _all_findings(self):
        out = []
        for r in self.results:
            for f in r.get("findings", []):
                out.append((r.get("agent", "?"), f))
        return out

    def answer(self, question):
        q = (question or "").strip().lower()
        if not q:
            return "Ask me about risk, stock, suppliers, costs, anomalies, trends, or type 'summary'."
        if not self.results:
            return "No analysis yet. Run analysis first."

        if any(k in q for k in ("summary", "overview", "report")):
            return self._summary()
        if "risk" in q:
            return self._metric("RiskAgent", "risk_score", "Risk score")
        if "stock" in q or "inventory" in q:
            return self._metric("InventoryAgent", "low_stock_skus", "Low-stock SKUs")
        if "supplier" in q:
            return self._metric("SupplierAgent", "supplier_count", "Suppliers")
        if "cost" in q or "price" in q:
            return self._metric("CostAgent", "avg_cost", "Average cost")
        if "anomal" in q or "outlier" in q:
            return self._metric("AnomalyAgent", "total_anomalies", "Detected anomalies")
        if "trend" in q:
            t = self._find("TrendAgent")
            if t:
                m = t.get("metrics", {})
                return "Trend direction: " + str(m.get("direction", "n/a")) + \
                       " (R2=" + str(m.get("r2", "n/a")) + ")"
            return "Trend agent not run."
        if "correlat" in q:
            c = self._find("CorrelationAgent")
            if c:
                return "Strong pairs: " + str(c.get("metrics", {}).get("strong_pairs", 0)) + \
                       ", top: " + str(c.get("metrics", {}).get("top_pair", "n/a"))
            return "Correlation agent not run."
        if "reorder" in q or "eoq" in q or "safety" in q:
            r = self._find("ReorderAgent")
            if r:
                m = r.get("metrics", {})
                return "ROP=" + str(m.get("reorder_point", "n/a")) + \
                       ", Safety stock=" + str(m.get("safety_stock_95", "n/a")) + \
                       ", EOQ=" + str(m.get("eoq_units", "n/a"))
            return "Reorder agent not run."
        if "sentiment" in q:
            return self._metric("SentimentAgent", "avg_sentiment", "Average sentiment")
        if "lead" in q or "delay" in q:
            return self._metric("LeadTimeAgent", "avg_lead_time", "Average lead time (days)")

        # fallback: keyword match findings
        hits = [f for a, f in self._all_findings() if any(w in f.lower() for w in q.split()[:3])]
        if hits:
            return "Related findings:\n- " + "\n- ".join(hits[:6])
        return "I could not match that. Try: risk, stock, supplier, cost, anomaly, trend, reorder, sentiment."

    def _summary(self):
        lines = []
        for r in self.results:
            m = r.get("metrics", {})
            bits = ", ".join(str(k) + "=" + str(v) for k, v in list(m.items())[:3])
            lines.append("- " + str(r.get("agent")) + ": " + str(r.get("summary", "")) +
                         (" | " + bits if bits else ""))
        return "\n".join(lines) if lines else "No results."

    def _metric(self, agent, key, label):
        r = self._find(agent)
        if not r:
            return agent + " was not run."
        v = r.get("metrics", {}).get(key)
        return label + ": " + (str(v) if v is not None else "n/a")
