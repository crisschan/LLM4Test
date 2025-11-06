from enum import Enum
from typing import List

from queryrewrite.utils.data_models import RewrittenQuery
from .validators import (
    no_validation,
    rouge_l_bleu_normalized,
    pareto_optimal,
    most_detailed,
    llm_semantic_similarity,
    filter_by_rouge_l_bleu_thresholds,
    
)
from queryrewrite.llm.base import LLMBase

class ValidationMethod(Enum):
    NONE = "none"
    ROUGE_L_BLEU_NORMALIZED = "rouge_l_bleu_normalized"
    PARETO_OPTIMAL = "pareto_optimal"
    MOST_DETAILED = "most_detailed"
    LLM_SEMANTIC_SIMILARITY = "llm_semantic_similarity"
    FILTER_BY_ROUGE_L_BLEU_THRESHOLDS = "filter_by_rouge_l_bleu_thresholds"

def validate(
    method: ValidationMethod,
    rewritten_queries: List[RewrittenQuery],
    original_query: str,
    llm: LLMBase = None,
    thinking:str=''
) -> List[RewrittenQuery]:
    """
    Unified entry point for query validation.

    Args:
        method: The validation method to use.
        rewritten_queries: The list of rewritten queries to validate.
        original_query: The original query string.
        llm: The LLM instance to use for LLM-based validation.

    Returns:
        A list of validated queries.
    """
    if method == ValidationMethod.NONE:
        return no_validation(rewritten_queries, original_query)
    elif method == ValidationMethod.ROUGE_L_BLEU_NORMALIZED:
        return rouge_l_bleu_normalized(rewritten_queries, original_query)
    elif method == ValidationMethod.PARETO_OPTIMAL:
        return pareto_optimal(rewritten_queries, original_query)
    elif method == ValidationMethod.MOST_DETAILED:
        return most_detailed(rewritten_queries, original_query)
    elif method == ValidationMethod.LLM_SEMANTIC_SIMILARITY:
        if not llm:
            raise ValueError("LLM instance is required for this validation method.")
        return llm_semantic_similarity(rewritten_queries, original_query, llm,thinking)
    elif method == ValidationMethod.FILTER_BY_ROUGE_L_BLEU_THRESHOLDS:
        return filter_by_rouge_l_bleu_thresholds(rewritten_queries, original_query)
    else:
        raise ValueError(f"Unknown validation method: {method}")
