import itertools
from typing import List
import json
import random

try:
    import jieba.posseg as pseg
    HAS_JIEBA = True
except ImportError:
    HAS_JIEBA = False
    print("Warning: jieba not installed, falling back to simple split. Install jieba for Chinese POS support.")

from queryrewrite.llm.base import LLMBase
from queryrewrite.utils.data_models import Query, RewrittenQuery
from queryrewrite.utils.super_list import SuperList

class SynonymRewriter:
    """通过调用LLM为查询中的词语生成同义词，从而重写查询。"""

    def __init__(self, llm: LLMBase, thinking: str = '', max_combos: int = 50, max_synonyms_per_word: int = 5):
        """
        参数:
            llm: 大语言模型实例。
            thinking: 可选的思考或引导提示。
            max_combos: 生成重写查询的最大数量。
            max_synonyms_per_word: 为单个词生成的同义词上限，用于控制组合爆炸。
        """
        self.llm = llm
        self.thinking = thinking
        self.max_combos = max_combos
        self.max_synonyms_per_word = max_synonyms_per_word

    def _tokenize_pos(self, text: str) -> List[tuple]:
        """带词性标注的分词：如果jieba可用则使用，否则使用带模拟词性的简单拆分。"""
        if HAS_JIEBA:
            return list(pseg.cut(text))
        else:
            # 后备方案：简单拆分，模拟词性（'n'代表名词/动词，'x'代表其他）
            words = text.split()
            return [(w, 'n' if len(w) > 1 else 'x') for w in words]

    def _get_synonyms(self, word: str, flag: str) -> List[str]:
        """通过LLM获取同义词，如果词性是标点/未知则跳过。"""
        skip_flags = ['x', 'wp', 'ws', 'w']  # 常见的跳过标记：未知/标点/空格
        if flag in skip_flags:
            return [word]  # 跳过LLM，保留原词

        prompt = f"{self.thinking}\\n\\n生成‘{word}’的最多{self.max_synonyms_per_word}个同义词，以json list的格式返回。"
        response = self.llm.invoke(prompt)
        
        try:
            synonyms = SuperList(response)
            # 限制数量并确保是字符串列表
            synonyms = [s.strip() for s in synonyms[:self.max_synonyms_per_word] if isinstance(s, str) and s]
            return synonyms if synonyms else [word]
        except Exception as e:
            print(f"为'{word}'生成同义词失败: {e}，回退到原词。")
            return [word]

    def rewrite(self, query: Query) -> List[RewrittenQuery]:
        """
        通过为其词语生成同义词来重写查询。

        参数:
            query: 要重写的查询对象（使用 .query 和 .reference 属性）。

        返回:
            一个重写后的查询列表（List[RewrittenQuery]，数量有上限）。
        """
        if not query["query"].strip():
            return []

        words_pos = self._tokenize_pos(query["query"])
        rewritten_word_lists = []
        for word, flag in words_pos:
            synonyms = self._get_synonyms(word, flag)
            rewritten_word_lists.append(synonyms)

        # 生成组合，如果太多则进行采样
        all_combos = list(itertools.product(*rewritten_word_lists))
        num_combos = len(all_combos)
        if num_combos > self.max_combos:
            print(f"警告: {num_combos} 个组合超过了最大值 {self.max_combos}；将进行采样。")
            all_combos = random.sample(all_combos, self.max_combos)

        rewritten_queries = []
        for combination in all_combos:
            # 智能拼接：对中文类查询不加空格，对混合/英文查询加空格
            joined_query = "".join(combination) if all(len(w) > 1 and not w.isascii() for w in combination) else " ".join(combination)
            rewritten_queries.append(
                {"query": joined_query, "reference": query["reference"]}
            )

        return rewritten_queries
