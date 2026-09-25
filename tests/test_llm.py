from app.llm.ollama_provider import OllamaProvider


def test_ollama_provider():
    provider = OllamaProvider()

    response = provider.generate(
        system_prompt=("You are a concise support assistant."),
        user_prompt=("Reply with exactly: TicketIQ LLM works."),
    )

    assert "TicketIQ LLM works." in response
