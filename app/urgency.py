CATEGORY_WEIGHT = {
    "billing": 0.5,
    "technical": 0.7,
    "account": 0.6,
    "feature_request": 0.2,
}

TIER_WEIGHT = {
    "basic": 0.2,
    "standard": 0.5,
    "premium": 0.8,
}


def sentiment_to_score(sentiment: str, score: float) -> float:
    """
    Convert VADER sentiment into an urgency contribution.

    Negative sentiment increases urgency.
    Positive sentiment decreases urgency.
    Neutral sentiment has no sentiment contribution.
    """

    if sentiment == "negative":
        return abs(score)

    if sentiment == "positive":
        return 0.0

    return 0.2


def calculate_urgency(
    category: str,
    sentiment_data: dict,
    tier: str,
) -> dict:
    """
    Calculate a normalized urgency score between 0 and 1.

    Urgency depends on:
    - ticket category
    - strongest negative aspect sentiment
    - customer tier
    """

    category_score = CATEGORY_WEIGHT.get(
        category,
        0.5,
    )

    tier_score = TIER_WEIGHT.get(
        tier.lower(),
        0.5,
    )

    aspect_scores = []

    for aspect in sentiment_data.get("aspects", {}).values():
        aspect_scores.append(
            sentiment_to_score(
                aspect["sentiment"],
                aspect["score"],
            )
        )

    if aspect_scores:
        sentiment_score = max(aspect_scores)
    else:
        sentiment_score = sentiment_to_score(
            sentiment_data["overall"]["sentiment"],
            sentiment_data["overall"]["score"],
        )

    urgency = 0.4 * category_score + 0.4 * sentiment_score + 0.2 * tier_score

    urgency = max(0.0, min(1.0, urgency))

    if urgency >= 0.75:
        level = "critical"
    elif urgency >= 0.50:
        level = "high"
    elif urgency >= 0.25:
        level = "medium"
    else:
        level = "low"

    return {
        "score": round(urgency, 4),
        "level": level,
        "components": {
            "category": round(category_score, 4),
            "sentiment": round(sentiment_score, 4),
            "tier": round(tier_score, 4),
        },
    }
