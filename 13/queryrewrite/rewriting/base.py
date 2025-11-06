from enum import Enum
from typing import List, Dict, Any

from queryrewrite.utils.data_models import Query, RewrittenQuery, Glossary
from .llm_rewriter import LLMRewriter
from .glossary_rewriter import GlossaryRewriter
from .synonym_rewriter import SynonymRewriter

class RewriteMethod(Enum):
    LLM = "llm"
    GLOSSARY = "glossary"
    SYNONYM = "synonym"

def rewrite(
    method: RewriteMethod,
    query: Query,
    glossary: Glossary = None,
    llm = None,
    thinking: str = ''
) -> List[RewrittenQuery]:
    """
    Unified entry point for query rewriting.

    Args:
        method: The rewriting method to use.
        query: The input query to rewrite.
        glossary: The glossary to use for the GLOSSARY method.
        llm: The LLM instance to use for LLM-based methods.

    Returns:
        A list of rewritten queries.
    """
    if method == RewriteMethod.LLM:
        if not llm:
            raise ValueError("LLM instance is required for the LLM method.")
        rewriter = LLMRewriter(llm,thinking)
        return rewriter.rewrite(query)
    elif method == RewriteMethod.GLOSSARY:
        if not glossary:
            raise ValueError("Glossary is required for the GLOSSARY method.")
        rewriter = GlossaryRewriter(glossary)
        return rewriter.rewrite(query)
    elif method == RewriteMethod.SYNONYM:
        if not llm:
            raise ValueError("LLM instance is required for the SYNONYM method.")
        rewriter = SynonymRewriter(llm,thinking)
        return rewriter.rewrite(query)
    else:
        raise ValueError(f"Unknown rewrite method: {method}")
