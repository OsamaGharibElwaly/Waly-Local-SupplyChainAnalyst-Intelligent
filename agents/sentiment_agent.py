from agents.base_agent import BaseAgent
from config import THRESHOLDS

POSITIVE = {"good","great","excellent","satisfied","fast","reliable","perfect",
            "happy","prompt","amazing","recommend","quality","on time","love"}
NEGATIVE = {"bad","late","delay","poor","broken","damaged","slow","missing",
            "terrible","worst","angry","refund","problem","issue","defective"}


def score_text(text):
    if not isinstance(text, str):
        return 0.0
    words = text.lower().split()
    pos = sum(1 for w in words if w in POSITIVE)
    neg = sum(1 for w in words if w in NEGATIVE)
    total = pos + neg
    return 0.0 if total == 0 else (pos - neg) / total


class SentimentAgent(BaseAgent):
    name = "SentimentAgent"
    description = "Sentiment analysis (lexicon, local)"

    def run(self):
        findings, metrics = [], {}
        text_col = self._safe_col("review", "feedback", "comment", "notes", "description")
        if text_col and self.can_run():
            scores = self.df[text_col].apply(score_text)
            avg = float(scores.mean())
            metrics["avg_sentiment"] = round(avg, 3)
            metrics["positive_count"] = int((scores > 0.1).sum())
            metrics["negative_count"] = int((scores < -0.1).sum())
            metrics["neutral_count"] = int(len(scores) - metrics["positive_count"] - metrics["negative_count"])
            findings.append(f"Avg sentiment: {avg:+.2f}")
            findings.append(f"Pos {metrics['positive_count']} / Neg {metrics['negative_count']} / Neu {metrics['neutral_count']}")
            if avg < THRESHOLDS["sentiment_negative"]:
                findings.append("⚠ Overall negative sentiment")
        if not findings:
            findings.append("No text column for sentiment")
        return {"agent": self.name, "summary": "Sentiment analysis",
                "findings": findings, "metrics": metrics}