import itertools
from typing import List
import random
import re

try:
    import jieba
    HAS_JIEBA = True
except ImportError:
    HAS_JIEBA = False
    print("Warning: jieba not installed, falling back to simple split. Install jieba for Chinese support.")

from queryrewrite.utils.data_models import Query, RewrittenQuery, Glossary

class GlossaryRewriter:
    """使用同义词词汇表重写查询。"""

    def __init__(self, glossary: Glossary, max_combos: int = 100):
        """
        参数:
            glossary: 同义词组列表，格式为 List[List[str]]。
            max_combos: 生成重写查询的最大数量（防止组合爆炸）。
        """
        self.glossary = glossary
        self.max_combos = max_combos
        self.synonym_map = self._create_synonym_map()
        if HAS_JIEBA:
            self._add_glossary_to_jieba()

    def _create_synonym_map(self) -> dict:
        """创建映射：单词 -> 完整的同义词列表。"""
        synonym_map = {}
        for word_list in self.glossary:
            for word in word_list:
                synonym_map[word] = word_list
        return synonym_map

    def _add_glossary_to_jieba(self):
        """将词汇表中的词（去重后）添加到jieba词典。"""
        unique_words = set(word for word_list in self.glossary for word in word_list)
        for word in unique_words:
            jieba.add_word(word)

    def _tokenize(self, text: str) -> List[str]:
        """查询分词：如果jieba可用则使用jieba，否则使用简单拆分。"""
        if HAS_JIEBA:
            return list(jieba.cut(text))
        else:
            # 后备方案：按空格/标点符号拆分，比较粗糙但适用于混合语言
            return re.findall(r'\w+|[^\w\s]', text, re.UNICODE)

    def rewrite(self, query: Query) -> List[RewrittenQuery]:
        """
        使用词汇表重写查询。

        参数:
            query: 要重写的查询对象（使用 .query 和 .reference 属性）。

        返回:
            一个重写后的查询列表（List[RewrittenQuery]，数量上限为 max_combos）。
        """
        if not query["query"].strip():
            return []  # 边缘情况：处理空查询

        words = self._tokenize(query["query"])
        rewritten_word_lists = [self.synonym_map.get(word, [word]) for word in words]

        # 生成所有组合，如果数量过多则进行采样
        all_combos = list(itertools.product(*rewritten_word_lists))
        num_combos = len(all_combos)
        if num_combos > self.max_combos:
            print(f"警告: 组合数 {num_combos} 超出最大值 {self.max_combos}；将进行随机采样。")
            all_combos = random.sample(all_combos, self.max_combos)

        rewritten_queries = []
        for combination in all_combos:
            # 拼接：对纯中文不使用空格，对英文/混合使用空格（启发式）
            is_chinese_like = all(re.match(r'[\u4e00-\u9fff]', w) for w in combination if w.strip())
            joined_query = "".join(combination) if is_chinese_like else " ".join(combination)
            
            rewritten_queries.append(
                {"query": joined_query, "reference": query["reference"]}
            )

        return rewritten_queries
