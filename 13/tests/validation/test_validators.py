import pytest
from unittest.mock import MagicMock

from queryrewrite.validation.validators import (
    no_validation,
    rouge_l_bleu_normalized,
    pareto_optimal,
    most_detailed,
    llm_semantic_similarity,
)
from queryrewrite.utils.data_models import RewrittenQuery


@pytest.fixture
def rewritten_queries() -> list[RewrittenQuery]:
    """Fixture for a list of rewritten queries."""
    return [
        {"query": "重写的查询1", "reference": "测试参考"},
        {"query": "重写的查询2更长一些", "reference": "测试参考"},
    ]


def test_no_validation(rewritten_queries):
    """Tests the no_validation validator."""
    result = no_validation(rewritten_queries, "原始查询")
    assert result == rewritten_queries


def test_rouge_l_bleu_normalized(rewritten_queries):
    """Tests the rouge_l_bleu_normalized validator."""
    result = rouge_l_bleu_normalized(rewritten_queries, "原始查询")
    assert len(result) == 1


def test_pareto_optimal(rewritten_queries):
    """Tests the pareto_optimal validator."""
    result = pareto_optimal(rewritten_queries, "原始查询")
    # This is a more complex test, for simplicity we'll just check it returns something
    assert len(result) > 0


def test_most_detailed(rewritten_queries):
    """Tests the most_detailed validator."""
    result = most_detailed(rewritten_queries, "原始查询")
    assert len(result) == 1
    assert result[0]["query"] == "重写的查询2更长一些"


def test_llm_semantic_similarity(rewritten_queries):
    """Tests the llm_semantic_similarity validator."""
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = "0.8"
    result = llm_semantic_similarity(rewritten_queries, "原始查询", mock_llm)
    assert len(result) == 1
