from typing import List

from queryrewrite.utils.data_models import RewrittenQuery
from .metrics import calculate_rouge_l, calculate_bleu
from queryrewrite.llm.base import LLMBase
from queryrewrite.utils.super_float import SuperFloat

def no_validation(rewritten_queries: List[RewrittenQuery], original_query: str) -> List[RewrittenQuery]:
    """Returns the rewritten queries without any validation."""
    return rewritten_queries

def rouge_l_bleu_normalized(rewritten_queries: List[RewrittenQuery], original_query: str, rouge_weight: float = 0.7) -> List[RewrittenQuery]:
    """
    通过加权的ROUGE-L和(1-BLEU)分数来选择最佳查询。
    ROUGE-L (越高越好) 代表语义相似度。
    BLEU (越低越好) 代表词汇差异度。我们使用 (1-BLEU) 使其变为越高越好。
    """
    if not rewritten_queries:
        return []

    if not (0 <= rouge_weight <= 1):
        raise ValueError("rouge_weight must be between 0 and 1.")
    bleu_weight = 1 - rouge_weight

    scored_queries = []
    for rq in rewritten_queries:
        rouge_l = calculate_rouge_l(rq["query"], original_query)
        bleu = calculate_bleu(rq["query"], original_query)
        # 综合得分：ROUGE-L越高越好，BLEU越低越好 (1-BLEU)
        score = rouge_weight * rouge_l + bleu_weight * (1 - bleu)
        scored_queries.append((score, rq))

    if not scored_queries:
        return []

    # 返回综合得分最高的查询
    best_query = max(scored_queries, key=lambda item: item[0])
    return [best_query[1]]

def filter_by_rouge_l_bleu_thresholds(rewritten_queries: List[RewrittenQuery], original_query: str, 
                        rouge_l_threshold: float = 0.4, bleu_threshold: float = 0.3) -> List[RewrittenQuery]:
    """
    Filters queries based on ROUGE-L and BLEU score thresholds.
    
    Returns queries where:
    - ROUGE-L score > rouge_l_threshold (higher is better)
    - BLEU score < bleu_threshold (lower is better)
    
    Args:
        rewritten_queries: List of rewritten queries to filter
        original_query: The original query for comparison
        rouge_l_threshold: Minimum ROUGE-L score threshold (default: 0.4)
        bleu_threshold: Maximum BLEU score threshold (default: 0.3)
        
    Returns:
        List of queries that meet both threshold criteria
    """
    if not rewritten_queries:
        return []

    optimal_queries = []
    
    for rq in rewritten_queries:
        rouge_l_score = calculate_rouge_l(rq["query"], original_query)
        bleu_score = calculate_bleu(rq["query"], original_query)
        # print(f"Query: {rq['query']}, ROUGE-L: {rouge_l_score}, BLEU: {bleu_score}")
        # Check if query meets both criteria:
        # - ROUGE-L score >= threshold (higher semantic similarity)
        # - BLEU score < threshold (lower lexical similarity)
        if rouge_l_score >= rouge_l_threshold and bleu_score < bleu_threshold:
            optimal_queries.append(rq)
    
    return optimal_queries

def pareto_optimal(rewritten_queries: List[RewrittenQuery], original_query: str) -> List[RewrittenQuery]:
    """Finds the Pareto optimal set of rewritten queries based on ROUGE-L and BLEU scores."""
    if not rewritten_queries:
        return []

    scores = []
    for rq in rewritten_queries:
        rouge_l = calculate_rouge_l(rq["query"], original_query)
        bleu = calculate_bleu(rq["query"], original_query)
        scores.append((rouge_l, bleu, rq))

    pareto_front = []
    for i, (r1, b1, q1) in enumerate(scores):
        is_dominated = False
        for j, (r2, b2, q2) in enumerate(scores):
            if i == j: continue
            # A query is dominated if another query is better or equal in all objectives
            # and strictly better in at least one objective.
            if (r2 >= r1 and b2 <= b1) and (r2 > r1 or b2 < b1):
                is_dominated = True
                break
        if not is_dominated:
            pareto_front.append(q1)
            
    return pareto_front

def most_detailed(rewritten_queries: List[RewrittenQuery], original_query: str) -> List[RewrittenQuery]:
    """返回最长的查询。如果没有重写查询，则返回空列表。"""
    if not rewritten_queries:
        return []
    # 返回所有查询中最长的一个
    return [max(rewritten_queries, key=lambda rq: len(rq["query"]))]

def llm_semantic_similarity(rewritten_queries: List[RewrittenQuery], original_query: str, llm: LLMBase,thinking:str='') -> List[RewrittenQuery]:
    """使用LLM寻找语义最相似且词汇差异最大（BLEU最低）的查询。"""
    if not rewritten_queries:
        return []

    best_query = None
    highest_similarity = -1.0
    lowest_bleu_at_highest_sim = 2.0  # BLEU 分数在 0 和 1 之间

    for rq in rewritten_queries:
        prompt = f'{thinking}\n\n评估以下两个查询的语义相似度，\n查询1: {original_query}\n查询2: {rq["query"]}，返回一个0到1之间的浮点数，semantic_similarity=。'
        response = llm.invoke(prompt)
        try:
            similarity = SuperFloat(response)
            bleu_score = calculate_bleu(rq["query"], original_query)
            
            # 核心选择逻辑：
            # 1. 如果当前查询的相似度更高，则更新最佳查询。
            # 2. 如果相似度相等，则选择BLEU分数更低的那个（词汇差异更大）。
            if similarity > highest_similarity:
                highest_similarity = similarity
                lowest_bleu_at_highest_sim = bleu_score
                best_query = rq
            elif abs(similarity - highest_similarity) < 1e-9:  # 处理浮点数相等的情况
                if bleu_score < lowest_bleu_at_highest_sim:
                    lowest_bleu_at_highest_sim = bleu_score
                    best_query = rq
        except Exception as e:
            print(f"Error processing similarity for query '{rq['query']}': {e}")
            continue

    return [best_query] if best_query else []
