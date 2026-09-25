from app.urgency import calculate_urgency


def test_critical_technical_ticket():
    sentiment = {
        "aspects": {
            "technical": {
                "sentiment": "negative",
                "score": -0.9,
            }
        },
        "overall": {
            "sentiment": "negative",
            "score": -0.9,
        },
    }

    result = calculate_urgency(
        category="technical",
        sentiment_data=sentiment,
        tier="premium",
    )

    assert result["score"] > 0.7
    assert result["level"] == "critical"


def test_low_feature_request():
    sentiment = {
        "aspects": {
            "feature": {
                "sentiment": "positive",
                "score": 0.5,
            }
        },
        "overall": {
            "sentiment": "positive",
            "score": 0.5,
        },
    }

    result = calculate_urgency(
        category="feature_request",
        sentiment_data=sentiment,
        tier="basic",
    )

    assert result["score"] < 0.4
