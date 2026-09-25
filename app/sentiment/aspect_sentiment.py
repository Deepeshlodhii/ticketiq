from typing import ClassVar

from nltk.sentiment import SentimentIntensityAnalyzer


class AspectSentimentAnalyzer:
    """
    Lightweight aspect-level sentiment analyzer.

    1. Detects known support-ticket aspects using keywords.
    2. Uses VADER to calculate sentiment for the ticket text.
    """

    ASPECT_KEYWORDS: ClassVar[dict[str, list[str]]] = {
        "billing": [
            "billing",
            "bill",
            "invoice",
            "charge",
            "charged",
            "payment",
            "refund",
            "price",
            "cost",
        ],
        "account": [
            "account",
            "login",
            "password",
            "verification",
            "access",
            "profile",
            "email",
        ],
        "technical": [
            "app",
            "application",
            "website",
            "error",
            "crash",
            "crashing",
            "bug",
            "loading",
            "server",
            "upload",
            "download",
            "search",
        ],
        "feature": [
            "feature",
            "integration",
            "export",
            "notification",
            "dashboard",
            "mobile",
            "language",
            "calendar",
            "api",
        ],
        "service": [
            "service",
            "support",
            "help",
            "response",
            "experience",
        ],
    }

    def __init__(self):
        self.sentiment_analyzer = SentimentIntensityAnalyzer()

    def _detect_aspects(self, text: str) -> list[str]:
        text_lower = text.lower()

        detected = []

        for aspect, keywords in self.ASPECT_KEYWORDS.items():
            if any(keyword in text_lower for keyword in keywords):
                detected.append(aspect)

        return detected

    def _get_sentiment(self, text: str) -> dict:
        scores = self.sentiment_analyzer.polarity_scores(text)

        compound = scores["compound"]

        if compound >= 0.05:
            label = "positive"
        elif compound <= -0.05:
            label = "negative"
        else:
            label = "neutral"

        return {
            "sentiment": label,
            "score": round(compound, 4),
        }

    def analyze(self, text: str) -> dict:
        aspects = self._detect_aspects(text)

        overall_sentiment = self._get_sentiment(text)

        result = {}

        for aspect in aspects:
            result[aspect] = overall_sentiment.copy()

        return {
            "aspects": result,
            "overall": overall_sentiment,
        }
