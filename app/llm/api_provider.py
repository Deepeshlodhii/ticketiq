from app.llm.base import LLMProvider


class APIProvider(LLMProvider):
    """
    Placeholder for a future hosted LLM provider.

    The rest of TicketIQ does not need to know which
    provider is being used.
    """

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        raise NotImplementedError("Hosted API provider is not configured.")
