# 为大模型应用测试提供Query 改写的工具：query rewrite

## 项目简介

大模型应用测试提供最需要的就是query改写，也有叫问题改写，query扩写等等，其实都是为了在有限的测试数据之下快速扩充测试数据，让测试数据更加丰富。
queryrewrite是就是一个提供如上功能的Python库，它提供了多种方法来rewrite和验证查询，以提高搜索和检索系统的性能。该项目支持使用大型语言模型（LLM）、词汇表替换和同义词替换等方法进行查询重写，并提供多种验证方法来确保重写后的查询保持原始语义。
## 安装

### 环境要求

- Python >= 3.10

### 安装步骤

```bash
# 克隆仓库
git clone https://github.com/yourusername/queryrewrite.git
cd queryrewrite

# 安装依赖
pip install -e .
```

或者直接通过pip安装：

```bash
pip install queryrewrite
```

## 功能介绍

Query Rewrite 项目提供以下主要功能：

1. **query改写**：使用多种方法重写原始查询，生成语义相似但表达不同的查询变体
2. **改写query验证和筛选**：使用多种方法验证改写后的query，确保它们与原始query保持语义一致性，去除质量较差的改写
3. **LLM集成**：支持与多种大型语言模型集成，如Ollama提供的模型
4. **中文支持**：特别优化了对中文文本的处理，包括分词和相似度计算

## query改写方法

### 1. LLM改写 (RewriteMethod.LLM)

利用大型语言模型（如Qwen、Llama等）重写查询。这种方法可以生成语义相似但表达方式不同的查询变体，有助于捕获用户意图的不同表达方式。

### 2. 词汇表改写 (RewriteMethod.GLOSSARY)

基于预定义的词汇表进行查询重写。词汇表包含同义词组，系统会使用这些同义词替换原始查询中的关键词，生成多个查询变体。这种方法适用于有明确领域词汇的场景。

### 3. 同义词改写 (RewriteMethod.SYNONYM)

使用LLM生成原始查询中关键词的同义词，然后用这些同义词替换原始查询中的关键词，生成多个查询变体。这种方法结合了LLM的语义理解能力和词汇替换的精确性。

## query验证和筛选方法

### 1. 无验证 (ValidationMethod.NONE)

不进行任何验证，直接返回所有重写后的查询。适用于已经确信重写质量的场景，或者需要最大化查询多样性的情况。

### 2. ROUGE-L和BLEU归一化验证 (ValidationMethod.ROUGE_L_BLEU_NORMALIZED)

使用ROUGE-L和BLEU分数来评估改写的query与原始query的相似度，并选择最佳平衡点。这种方法既考虑了语义保留又考虑了表达多样性（BLEU）。

### 3. 帕累托最优 (ValidationMethod.PARETO_OPTIMAL)

应用帕累托最优原则，选择在ROUGE-L和BLEU分数上都不被其他查询支配的查询。这种方法可以找到语义保留和表达多样性的最佳平衡点。

### 4. 最详细 (ValidationMethod.MOST_DETAILED)

选择最详细（通常是最长）的重写查询。这种方法假设更详细的查询通常包含更多信息，可能更好地捕获用户意图。

### 5. ROUGE-L + BLEU阈值过滤 (ValidationMethod.FILTER_BY_ROUGE_L_BLEU_THRESHOLDS)

根据预设的ROUGE-L和BLEU阈值过滤重写查询。只有同时满足ROUGE-L最小阈值（确保语义相似性）和BLEU最大阈值（确保表达多样性）的查询才会被保留。

### 6. LLM语义相似度 (ValidationMethod.LLM_SEMANTIC_SIMILARITY)

利用LLM评估改写query与原始query的语义相似度。这种方法利用LLM的语义理解能力，可以捕获更复杂的语义关系，但计算成本较高。

## 使用示例

以下是使用queryrewrite库的完整示例：

```python
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

    # 1. 初始化LLM
    # 这里假设你已经运行了Ollama实例，并加载了qwen3:8b模型
    try:
        llm = OllamaLLM(model="qwen3:8b")
    except Exception as e:
        print(f"Error initializing Ollama LLM: {e}")
        print("Please ensure Ollama is running and the model is available.")
        return

    # 2. 定义输入查询
    query: Query = {"query": "如何测试一个大型语言模型？", "reference": "大型语言模型的测试是一个复杂的过程，涉及多个层面。"}

    # 3. 演示重写方法
    print("--- Demonstrating Rewriting Methods ---")

    # 方法1: LLM重写器
    print("\n--- Method 1: LLM Rewriter ---")
    try:
        llm_rewritten = rewrite(method=RewriteMethod.LLM, query=query, llm=llm,thinking='/no_think')
        print(f"LLM Rewritten Queries: {llm_rewritten}")
    except Exception as e:
        print(f"Error during LLM rewriting: {e}")

    # 方法2: 词汇表重写器
    print("\n--- Method 2: Glossary Rewriter ---")
    glossary: Glossary = [
        ["测试", "评估", "评测"],
        ["大型语言模型", "大模型", "LLM"],
    ]
    glossary_rewritten = rewrite(method=RewriteMethod.GLOSSARY, query=query, glossary=glossary)
    print(f"Glossary Rewritten Queries: {glossary_rewritten}")

    # 方法3: 同义词重写器
    print("\n--- Method 3: Synonym Rewriter ---")
    try:
        synonym_rewritten = rewrite(method=RewriteMethod.SYNONYM, query=query, llm=llm,thinking='/no_think')
        print(f"Synonym Rewritten Queries: {synonym_rewritten}")
    except Exception as e:
        print(f"Error during synonym rewriting: {e}")


    # 4. 演示验证方法
    print("\n--- Demonstrating Validation Methods ---")
    # 我们将使用glossary_rewritten列表进行验证示例
    rewritten_queries = glossary_rewritten

    # 方法1: 无验证
    print("\n--- Validation Method 1: No Validation ---")
    no_validation_result = validate(
        method=ValidationMethod.NONE,
        rewritten_queries=rewritten_queries,
        original_query=query["query"]
    )
    print(f"No Validation Result: {no_validation_result}")

    # 方法2: ROUGE-L + BLEU归一化
    print("\n--- Validation Method 2: ROUGE-L + BLEU Normalized ---")
    rouge_bleu_result = validate(
        method=ValidationMethod.ROUGE_L_BLEU_NORMALIZED,
        rewritten_queries=rewritten_queries,
        original_query=query["query"]
    )
    print(f"ROUGE-L + BLEU Normalized Result: {rouge_bleu_result}")

    # 方法3: 帕累托最优
    print("\n--- Validation Method 3: Pareto Optimal ---")
    pareto_result = validate(
        method=ValidationMethod.PARETO_OPTIMAL,
        rewritten_queries=rewritten_queries,
        original_query=query["query"]
    )
    print(f"Pareto Optimal Result: {pareto_result}")

    # 方法4: 最详细
    print("\n--- Validation Method 4: Most Detailed ---")
    detailed_result = validate(
        method=ValidationMethod.MOST_DETAILED,
        rewritten_queries=rewritten_queries,
        original_query=query["query"]
    )
    print(f"Most Detailed Result: {detailed_result}")
    
    # 方法5: 根据ROUGE-L + BLEU阈值过滤
    print("\n--- Validation Method 5: Filter by ROUGE-L + BLEU Thresholds ---")
    filtered_result = validate(
        method=ValidationMethod.FILTER_BY_ROUGE_L_BLEU_THRESHOLDS,
        rewritten_queries=rewritten_queries,
        original_query=query["query"]
    )
    print(f"Filtered Result: {filtered_result}")

    # 方法6: LLM语义相似度
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
```

## 如何扩展LLM

本项目设计了灵活的LLM接口，可以轻松扩展支持不同的大型语言模型。以下是如何添加OpenAI支持的示例。

### 1. 创建新的LLM实现类

首先，创建一个新的Python文件，例如`openai.py`，实现`LLMBase`抽象类：

```python
# queryrewrite/llm/openai.py
from langchain_openai import ChatOpenAI
from queryrewrite.llm.base import LLMBase

class OpenAILLM(LLMBase):
    """LLM implementation for OpenAI models."""

    def __init__(self, model: str = "gpt-3.5-turbo", api_key: str = None, temperature: float = 0.7):
        """
        Initializes the OpenAILLM.

        Args:
            model: The name of the OpenAI model to use.
            api_key: Your OpenAI API key.
            temperature: Controls randomness. Higher values make output more random,
                        lower values make it more deterministic.
        """
        self.model = model
        self.api_key = api_key
        self.temperature = temperature
        self.llm = ChatOpenAI(
            model=self.model,
            openai_api_key=self.api_key,
            temperature=self.temperature
        )

    def invoke(self, prompt: str) -> str:
        """Invoke the OpenAI model with a given prompt."""
        response = self.llm.invoke(prompt)
        return response.content
```

### 2. 安装必要的依赖

确保安装了OpenAI的依赖：

```bash
pip install langchain-openai openai
```

### 3. 使用新的LLM实现

现在，您可以在代码中使用OpenAI模型：

```python
from queryrewrite.llm.openai import OpenAILLM
from queryrewrite.rewriting.base import rewrite, RewriteMethod
from queryrewrite.utils.data_models import Query

# 初始化OpenAI LLM
llm = OpenAILLM(
    model="gpt-3.5-turbo",
    api_key="your-openai-api-key",  # 替换为您的API密钥
    temperature=0.7
)

# 定义查询
query = {"query": "如何测试一个大型语言模型？", "reference": "大型语言模型的测试是一个复杂的过程，涉及多个层面。"}

# 使用OpenAI进行查询重写
rewritten_queries = rewrite(method=RewriteMethod.LLM, query=query, llm=llm)
```

### 4. 扩展其他LLM提供商

您可以使用相同的模式扩展支持其他LLM提供商，如百度文心一言、讯飞星火等。只需：

1. 创建一个新的类，继承`LLMBase`
2. 实现`__init__`和`invoke`方法
3. 安装相应的依赖
4. 在您的代码中使用新的LLM实现

## 注意事项

- 使用LLM相关功能前，请确保已安装并运行相应的LLM服务（如Ollama）或配置正确的API密钥（如OpenAI）
- 对于中文查询，系统使用jieba进行分词处理，以提高相似度计算的准确性
- ROUGE-L和BLEU阈值可以根据具体应用场景进行调整
- 使用OpenAI等商业API时，请注意API使用成本和速率限制