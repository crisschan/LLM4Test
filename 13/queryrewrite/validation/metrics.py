# from rouge_score import rouge_scorer
from rouge_chinese import Rouge 
import jieba
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
import re

def calculate_rouge_l(candidate: str, reference: str) -> float:
    """
    Calculates the ROUGE-L F1 score for Chinese text using jieba for tokenization.
    """
    # Use jieba's precise mode for tokenization (default)
    candidate_tokens = " ".join(jieba.cut(candidate))
    reference_tokens = " ".join(jieba.cut(reference))

    # print(f"Candidate tokens: {candidate_tokens}")
    # print(f"Reference tokens: {reference_tokens}")

    # Initialize the scorer without stemming
    rouge = Rouge()
    scores = rouge.get_scores(candidate_tokens,reference_tokens)
    # print(scores)
    return scores[0]["rouge-l"]["f"]
def calculate_bleu(candidate: str, reference: str) -> float:
    """
    Calculates the BLEU score for Chinese text using jieba for tokenization.
    """
    # Use a regular expression to check for Chinese characters
    if not (re.search(r'[\u4e00-\u9fff]', reference) or re.search(r'[\u4e00-\u9fff]', candidate)):
        raise ValueError("This function is intended for Chinese text.")
    
    # Use jieba's precise mode (default) to get word lists
    reference_tokens = [list(jieba.cut(reference))]
    candidate_tokens = list(jieba.cut(candidate))
    
    # print(f"Reference tokens: {reference_tokens}")
    # print(f"Candidate tokens: {candidate_tokens}")
    
    # Use smoothing for more robust scoring, especially with short sentences
    chencherry = SmoothingFunction()
    return sentence_bleu(reference_tokens, candidate_tokens, smoothing_function=chencherry.method1)

# # 示例
# candidate_text = "今天天气非常好，阳光明媚。"
# reference_text = "今天天气很好，阳光灿烂。"

# rouge_score = calculate_rouge_l_zh(candidate_text, reference_text)
# bleu_score = calculate_bleu_zh(candidate_text, reference_text)

# print(f"中文 ROUGE-L F1 Score: {rouge_score:.4f}")
# print(f"中文 BLEU Score: {bleu_score:.4f}")