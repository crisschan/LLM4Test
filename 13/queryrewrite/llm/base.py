from abc import ABC, abstractmethod

class LLMBase(ABC):
    """Abstract base class for all LLM implementations."""

    @abstractmethod
    def invoke(self, prompt: str) -> str:
        """Invoke the LLM with a given prompt and return the response."""
        pass
