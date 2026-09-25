from app.sentiment.aspect_sentiment import AspectSentimentAnalyzer


def test_negative_ticket():
    analyzer = AspectSentimentAnalyzer()

    result = analyzer.analyze(
        "My payment was charged twice and the refund process is terrible."
    )

    assert "billing" in result["aspects"]
    assert result["overall"]["sentiment"] == "negative"


def test_positive_ticket():
    analyzer = AspectSentimentAnalyzer()

    result = analyzer.analyze(
        "The application is excellent and the support team was very helpful."
    )

    assert result["overall"]["sentiment"] == "positive"


def test_neutral_ticket():
    analyzer = AspectSentimentAnalyzer()

    result = analyzer.analyze("I want to change the email address on my account.")

    assert "account" in result["aspects"]
