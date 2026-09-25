from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Common interface for all LLM providers."""

    @abstractmethod
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        """Generate a response from the LLM."""
        raise NotImplementedError
