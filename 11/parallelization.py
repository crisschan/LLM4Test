import asyncio
import time
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
model_name = "gpt-oss:120b-cloud"
def get_ollama_response(prompt: str, model: str = model_name) -> str:
    """
    同步调用 Ollama 本地模型生成内容。
    """
    llm = OllamaLLM(model=model)
    prompt_template = PromptTemplate(
        input_variables=["prompt"],
        template="{prompt}"
    )
    response = (prompt_template | llm).invoke({"prompt": prompt})
    return response.strip()

async def generate_content(prompt: str, model: str = model_name) -> str:
    """
    用 asyncio.to_thread 将同步推理包装为异步。
    """
    return await asyncio.to_thread(get_ollama_response, prompt, model)

async def parallel_tasks(model: str = model_name) -> str:
    """
    并发执行多个测试报告生成任务，并聚合结果（模拟软件测试的Map-Reduce）。
    """
    llm = OllamaLLM(model=model)
    topic = "e-commerce app functionality testing"
    prompts = [
        f"Generate a short test report for user registration/login module in {topic}. Include: status (success/partial/fail), bug count, key metrics (e.g., response time), and fix suggestions. Keep it concise.",
        f"Generate a short test report for product search module in {topic}. Include: status (success/partial/fail), bug count, key metrics (e.g., accuracy rate), and fix suggestions. Keep it concise.",
        f"Generate a short test report for shopping cart module in {topic}. Include: status (success/partial/fail), bug count, key metrics (e.g., sync rate), and fix suggestions. Keep it concise.",
        f"Generate a short test report for payment module in {topic}. Include: status (success/partial/fail), bug count, key metrics (e.g., success rate), and fix suggestions. Keep it concise."
    ]
    # 并发执行所有推理任务（Map阶段：独立子任务并行）
    start_time = time.time()
    tasks = [generate_content(prompt, model) for prompt in prompts]
    results = await asyncio.gather(*tasks)
    end_time = time.time()
    print(f"Time taken for parallel testing: {end_time - start_time:.2f} seconds")
    print("\n--- Individual Test Reports ---")
    for i, result in enumerate(results):
        print(f"Report {i+1}: {result}\n")
    
    # 聚合结果（Reduce阶段：汇总成综合报告）
    test_reports = '\n'.join([f"Report {i+1}: {result}" for i, result in enumerate(results)])
    aggregation_prompt = PromptTemplate(
        input_variables=['test_reports'],
        template="""Based on the following four test reports for e-commerce app, create a cohesive summary. 
Include a Markdown table with columns: Module, Status, Bug Count, Key Metrics, Suggestions. 
Then, add a one-paragraph overall assessment and recommendations.
{test_reports}"""
    )
    aggregation_response = (aggregation_prompt | llm).invoke({"test_reports": test_reports})
    return aggregation_response

if __name__ == "__main__":
    result = asyncio.run(parallel_tasks())
    print(f"\n--- Aggregated Test Summary ---\n{result}")