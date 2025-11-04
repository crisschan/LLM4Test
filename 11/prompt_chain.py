from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate

# 初始化 Ollama LLM
llm1 = OllamaLLM(model="gpt-oss:120b-cloud")  # 你可以换成其他已拉取的模型名
llm2 = OllamaLLM(model="gpt-oss:120b-cloud")  # 你可以换成其他已拉取的模型名
# 示例用户故事（扩展为包含 Acceptance Criteria 的条目化描述）
user_story = """
story：作为用户，我希望能够登录系统后查看个人仪表盘，以便快速了解我的账户状态。
AC1: 用户输入有效的用户名和密码后，系统成功登录并重定向到个人仪表盘页面。
AC2: 仪表盘页面显示账户余额、最近交易记录和通知列表。
AC3: 如果登录凭证无效，系统显示错误消息并保持在登录页面。
AC4: 登录过程在5秒内完成，且仪表盘加载时间不超过3秒。
AC5: 用户注销后，无法访问仪表盘页面。
"""

# --- 步骤1：完善story ---
prompt1 = PromptTemplate(
    input_variables=["user_story"],
    template="""基于以下用户故事，完善story描述，包括生成详细的 Acceptance Criteria (AC)。
确保 AC 覆盖功能、非功能（如性能、安全）、正向/负向场景。
输出格式：用户故事 + Acceptance Criteria 列表 (AC1: ..., AC2: ... 等)。

用户故事：{user_story}"""
)
refined_story = (prompt1 | llm1).invoke({"user_story": user_story}).strip()
print("完善后的story：")
print(refined_story)

# --- 步骤2：基于步骤1输出生成测试用例 ---
prompt2 = PromptTemplate(
    input_variables=["refined_story"],
    template="""基于以下完善后的story及其 Acceptance Criteria，生成一个全面的测试用例列表，包括正向场景、负向场景和边界条件。
每个测试用例应包含：测试ID、描述、前置条件、步骤、预期结果。
输出格式为Markdown表格。

完善后的story：{refined_story}"""
)
test_cases = (prompt2 | llm2).invoke({"refined_story": refined_story}).strip()
print("\n生成的测试用例：")
print(test_cases)