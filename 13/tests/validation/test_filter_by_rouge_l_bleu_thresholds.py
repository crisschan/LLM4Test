import pytest
from queryrewrite.validation.validators import filter_by_rouge_l_bleu_thresholds
from queryrewrite.utils.data_models import RewrittenQuery


class TestRougeLBleuOptimal:
    """Test cases for filter_by_rouge_l_bleu_thresholds function."""
    
    def test_empty_queries(self):
        """Test with empty query list."""
        result = filter_by_rouge_l_bleu_thresholds([], "original query")
        assert result == []
    
    def test_basic_filtering(self):
        """Test basic filtering with default thresholds."""
        queries = [
            {"query": "如何测试大型语言模型", "reference": "test"},
            {"query": "测试大模型的方法", "reference": "test"},
            {"query": "完全不同的查询", "reference": "test"},
        ]
        
        original_query = "如何测试一个大型语言模型？"
        
        result = filter_by_rouge_l_bleu_thresholds(queries, original_query)
        
        # Should return queries that meet both criteria
        assert isinstance(result, list)
        assert all(isinstance(q, dict) for q in result)
        assert all("query" in q and "reference" in q for q in result)
    
    def test_custom_thresholds(self):
        """Test with custom threshold values."""
        queries = [
            {"query": "如何测试大型语言模型", "reference": "test"},
            {"query": "测试大模型的方法", "reference": "test"},
            {"query": "完全不同的查询", "reference": "test"},
        ]
        
        original_query = "如何测试一个大型语言模型？"
        
        # Use very strict thresholds
        result = filter_by_rouge_l_bleu_thresholds(queries, original_query, 
                                    rouge_l_threshold=0.8, bleu_threshold=0.2)
        
        # With strict thresholds, should return fewer or no results
        assert isinstance(result, list)
    
    def test_all_queries_filtered_out(self):
        """Test when all queries are filtered out."""
        queries = [
            {"query": "完全不同的查询", "reference": "test"},
            {"query": "另一个不相关的查询", "reference": "test"},
        ]
        
        original_query = "如何测试一个大型语言模型？"
        
        # Use very strict thresholds
        result = filter_by_rouge_l_bleu_thresholds(queries, original_query, 
                                    rouge_l_threshold=0.9, bleu_threshold=0.1)
        
        # Should return empty list when no queries meet criteria
        assert result == []
    
    def test_all_queries_pass(self):
        """Test when all queries pass the criteria."""
        queries = [
            {"query": "如何测试大型语言模型", "reference": "test"},
            {"query": "测试大模型的方法", "reference": "test"},
        ]
        
        original_query = "如何测试一个大型语言模型？"
        
        # Use very lenient thresholds
        result = filter_by_rouge_l_bleu_thresholds(queries, original_query, 
                                    rouge_l_threshold=0.0, bleu_threshold=0.9)
        
        # Should return all queries
        assert len(result) == len(queries)
    
    def test_threshold_logic(self):
        """Test that the threshold logic works correctly."""
        queries = [
            {"query": "如何测试大型语言模型", "reference": "test"},
            {"query": "测试大模型的方法", "reference": "test"},
            {"query": "完全不同的查询", "reference": "test"},
        ]
        
        original_query = "如何测试一个大型语言模型？"
        
        # Test with different threshold combinations
        result1 = filter_by_rouge_l_bleu_thresholds(queries, original_query, 
                                     rouge_l_threshold=0.3, bleu_threshold=0.7)
        result2 = filter_by_rouge_l_bleu_thresholds(queries, original_query, 
                                     rouge_l_threshold=0.5, bleu_threshold=0.5)
        
        # More strict thresholds should return fewer results
        assert len(result1) >= len(result2)
    
    def test_return_structure(self):
        """Test that returned queries have correct structure."""
        queries = [
            {"query": "如何测试大型语言模型", "reference": "test"},
        ]
        
        original_query = "如何测试一个大型语言模型？"
        
        result = filter_by_rouge_l_bleu_thresholds(queries, original_query)
        
        if result:  # If any queries pass the criteria
            query = result[0]
            assert "query" in query
            assert "reference" in query
            assert isinstance(query["query"], str)
            assert isinstance(query["reference"], str)