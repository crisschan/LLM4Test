#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This demo showcases the usage of the queryrewrite library.
"""

from queryrewrite.llm.ollama import OllamaLLM
from queryrewrite.rewriting.base import rewrite, RewriteMethod
from queryrewrite.validation.base import validate, ValidationMethod
from queryrewrite.utils.data_models import Query, Glossary

def main():
    """Main function to run the demo."""

    # 1. Initialize the LLM
    # This assumes you have an Ollama instance running with the llama3.1:8b model.
    try:
        llm = OllamaLLM(model="qwen3:8b")
    except Exception as e:
        print(f"Error initializing Ollama LLM: {e}")
        print("Please ensure Ollama is running and the model is available.")
        return

    # 2. Define the input query
    query: Query = {"query": "如何测试一个大型语言模型？", "reference": "大型语言模型的测试是一个复杂的过程，涉及多个层面。"}

    # 3. Demonstrate Rewriting Methods
    print("--- Demonstrating Rewriting Methods ---")

    # Method 1: LLM Rewriter
    print("\n--- Method 1: LLM Rewriter ---")
    try:
        llm_rewritten = rewrite(method=RewriteMethod.LLM, query=query, llm=llm,thinking='/no_think')
        print(f"LLM Rewritten Queries: {llm_rewritten}")
    except Exception as e:
        print(f"Error during LLM rewriting: {e}")

    # Method 2: Glossary Rewriter
    print("\n--- Method 2: Glossary Rewriter ---")
    glossary: Glossary = [
        ["测试", "评估", "评测"],
        ["大型语言模型", "大模型", "LLM"],
    ]
    glossary_rewritten = rewrite(method=RewriteMethod.GLOSSARY, query=query, glossary=glossary)
    print(f"Glossary Rewritten Queries: {glossary_rewritten}")

    # Method 3: Synonym Rewriter
    print("\n--- Method 3: Synonym Rewriter ---")
    try:
        synonym_rewritten = rewrite(method=RewriteMethod.SYNONYM, query=query, llm=llm,thinking='/no_think')
        print(f"Synonym Rewritten Queries: {synonym_rewritten}")
    except Exception as e:
        print(f"Error during synonym rewriting: {e}")


    # 4. Demonstrate Validation Methods
    print("\n--- Demonstrating Validation Methods ---")
    # We will use the glossary_rewritten list for validation examples
    rewritten_queries = glossary_rewritten

    # Method 1: No Validation
    print("\n--- Validation Method 1: No Validation ---")
    no_validation_result = validate(
        method=ValidationMethod.NONE,
        rewritten_queries=rewritten_queries,
        original_query=query["query"]
    )
    print(f"No Validation Result: {no_validation_result}")

    # Method 2: ROUGE-L + BLEU Normalized
    print("\n--- Validation Method 2: ROUGE-L + BLEU Normalized ---")
    rouge_bleu_result = validate(
        method=ValidationMethod.ROUGE_L_BLEU_NORMALIZED,
        rewritten_queries=rewritten_queries,
        original_query=query["query"]
    )
    print(f"ROUGE-L + BLEU Normalized Result: {rouge_bleu_result}")

    # Method 3: Pareto Optimal
    print("\n--- Validation Method 3: Pareto Optimal ---")
    pareto_result = validate(
        method=ValidationMethod.PARETO_OPTIMAL,
        rewritten_queries=rewritten_queries,
        original_query=query["query"]
    )
    print(f"Pareto Optimal Result: {pareto_result}")

    # Method 4: Most Detailed
    print("\n--- Validation Method 4: Most Detailed ---")
    detailed_result = validate(
        method=ValidationMethod.MOST_DETAILED,
        rewritten_queries=rewritten_queries,
        original_query=query["query"]
    )
    print(f"Most Detailed Result: {detailed_result}")
    # Method 5: Filter by ROUGE-L + BLEU Thresholds
    print("\n--- Validation Method 5: Filter by ROUGE-L + BLEU Thresholds ---")
    filtered_result = validate(
        method=ValidationMethod.FILTER_BY_ROUGE_L_BLEU_THRESHOLDS,
        rewritten_queries=rewritten_queries,
        original_query=query["query"]
    )
    print(f"Filtered Result: {filtered_result}")

    # Method 6: LLM Semantic Similarity
    print("\n--- Validation Method 6: LLM Semantic Similarity ---")
    try:
        llm_similarity_result = validate(
            method=ValidationMethod.LLM_SEMANTIC_SIMILARITY,
            rewritten_queries=rewritten_queries,
            original_query=query["query"],
            llm=llm,
            thinking='/no_think'
        )
        print(f"LLM Semantic Similarity Result: {llm_similarity_result}")
    except Exception as e:
        print(f"Error during LLM semantic similarity validation: {e}")

if __name__ == "__main__":
    main()
