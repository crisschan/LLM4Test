import pytest
from unittest.mock import MagicMock

from queryrewrite.llm.ollama import OllamaLLM

def test_ollama_llm_invoke(mocker):
    """Tests the invoke method of the OllamaLLM class."""
    # Arrange
    mock_ollama = MagicMock()
    mock_ollama.invoke.return_value = "rewritten query"
    mocker.patch("langchain_ollama.Ollama", return_value=mock_ollama)

    # Act
    llm = OllamaLLM()
    result = llm.invoke("test prompt")

    # Assert
    assert result == "rewritten query"
    mock_ollama.invoke.assert_called_once_with("test prompt")
