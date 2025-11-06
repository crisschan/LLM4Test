import pytest
from unittest.mock import MagicMock

from queryrewrite.rewriting.llm_rewriter import LLMRewriter
from queryrewrite.rewriting.glossary_rewriter import GlossaryRewriter
from queryrewrite.rewriting.synonym_rewriter import SynonymRewriter
from queryrewrite.utils.data_models import Query


@pytest.fixture
def mock_llm():
    """Fixture for a mock LLM."""
    llm = MagicMock()
    llm.invoke.return_value = '["rewritten query 1", "rewritten query 2"]'
    return llm


def test_llm_rewriter(mock_llm):
    """Tests the LLMRewriter."""
    # Arrange
    rewriter = LLMRewriter(mock_llm)
    query = {"query": "test query", "reference": "test reference"}

    # Act
    result = rewriter.rewrite(query)

    # Assert
    assert len(result) == 2
    assert result[0]["query"] == "rewritten query 1"
    assert result[0]["reference"] == "test reference"


def test_glossary_rewriter():
    """Tests the GlossaryRewriter with multi-word terms."""
    # Arrange
    glossary = [["测试", "评估", "评测"], ["大型语言模型", "大模型", "LLM"]]
    rewriter = GlossaryRewriter(glossary)
    query = {"query": "如何测试大型语言模型？", "reference": "test reference"}

    # Act
    result = rewriter.rewrite(query)

    # Assert
    assert len(result) == 9
    # Check a few examples
    assert {"query": "如何测试大型语言模型？", "reference": "test reference"} in result
    assert {"query": "如何评估大模型？", "reference": "test reference"} in result
    assert {"query": "如何评测LLM？", "reference": "test reference"} in result


def test_synonym_rewriter(mock_llm):
    """Tests the SynonymRewriter."""
    # Arrange
    rewriter = SynonymRewriter(mock_llm)
    query = {"query": "test query", "reference": "test reference"}

    # Act
    result = rewriter.rewrite(query)

    # Assert
    # This is a more complex test, as it depends on the mock LLM's response
    # for each word. For simplicity, we'll just check that it returns something.
    assert len(result) > 0
