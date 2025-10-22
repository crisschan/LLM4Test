import jieba

def lcs_length(x, y):
    """计算两个序列的最长公共子序列长度"""
    m, n = len(x), len(y)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if x[i-1] == y[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    return dp[m][n]

# 输入文本
reference = "讨论新产品发布计划，确定时间表为六月，分配市场团队设计广告，技术团队开发功能，预算需审批"
hypothesis = "讨论产品发布，六月为时间表，市场团队制做广告，技术团队负责功能开发"

# 分词
# jieba.add_word("xx")
ref_tokens = list(jieba.cut(reference.replace("，", ""), cut_all=False))
hyp_tokens = list(jieba.cut(hypothesis.replace("，", ""), cut_all=False))


# 调试：打印分词结果
print(f"Reference tokens: {ref_tokens}")
print(f"Hypothesis tokens: {hyp_tokens}")

# 计算 LCS 长度
lcs_len = lcs_length(ref_tokens, hyp_tokens)
print(lcs_len)
# 计算 ROUGE-L

m, n = len(ref_tokens), len(hyp_tokens)
precision = lcs_len / n if n > 0 else 0
recall = lcs_len / m if m > 0 else 0
f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

# 输出结果
print(f"ROUGE-L Precision: {precision:.3f}")
print(f"ROUGE-L Recall: {recall:.3f}")
print(f"ROUGE-L F1: {f1:.3f}")