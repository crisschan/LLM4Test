from langchain_ollama import OllamaLLM as Ollama
from queryrewrite.llm.base import LLMBase

class OllamaLLM(LLMBase):
    """LLM implementation for Ollama models."""

    def __init__(self, model: str = "llama3.1:8b", base_url: str = "http://localhost:11434"):
        """
        Initializes the OllamaLLM.

        Args:
            model: The name of the Ollama model to use.
            base_url: The base URL of the Ollama server.
        """
        self.model = model
        self.base_url = base_url
        self.llm = Ollama(model=self.model, base_url=self.base_url)

    def invoke(self, prompt: str) -> str:
        """Invoke the Ollama model with a given prompt."""
        return self.llm.invoke(prompt)
