import json  # 用于JSON数据的序列化和反序列化，处理测试计划和JaCoCo数据的输入/输出
from super_json import SuperJSON  # 增强JSON解析库，用于处理LLM可能返回的非标准JSON响应（如带Markdown的文本）
from pydantic import BaseModel  # 数据验证库，用于定义Evaluation模型，确保反馈结构化
import enum  # 枚举库，用于定义评估状态（PASS/FAIL），提高代码可读性和类型安全
from langchain_ollama import OllamaLLM  # LangChain的Ollama集成，用于本地LLM调用（qwen3:4b模型）
from langchain.prompts import PromptTemplate  # LangChain提示模板，用于构建动态prompt，提高LLM输入的结构化

# 定义评估状态枚举：PASS表示计划通过评估，FAIL表示需迭代优化
class EvaluationStatus(enum.Enum):
    PASS = "PASS"  
    FAIL = "FAIL"  

# 定义评估结果模型：使用Pydantic确保JSON响应严格匹配结构，避免解析错误
class Evaluation(BaseModel):
    evaluation: EvaluationStatus  # 评估结果：PASS或FAIL
    feedback: str  # 具体改进建议：如“增加payment模块case，缩短时长”
    reasoning: str  # 推理解释：为什么PASS/FAIL，基于JaCoCo风险和计划对比

# 模拟变更日志（实际项目中，可从Git diff、Jira API或文件加载，提供变更上下文）
CHANGE_LOG = """
- Updated login API: Added new OAuth flow in core module.  # 核心模块变更：优先测试OAuth流程
- Modified user profile endpoint: Fixed validation in utils package.  # 工具包修复：检查验证逻辑覆盖
- New feature in payment module: Integrated Stripe webhook.  # 新功能：高风险，需额外case覆盖webhook
- Bug fix in reporting service: Enhanced error logging.  # 报告服务修复：验证日志完整性
"""

# 模拟JaCoCo数据（实际从mcp-jacoco-server或XML解析获取，这里用文件级JSON数组格式）
JACOCO_DATA = [
    {  
        "sourcefile": "PasswordUtil.java",
        "package": "com/cicc/ut/util",
        "lines": {
            "nocovered": [],  
            "partiallycovered": []  
        },
        "branch": {
            "nocovered": [],
            "partiallycovered": []
        }
    },
    { 
        "sourcefile": "UserServiceImpl.java",
        "package": "com/cicc/ut/service/impl",
        "lines": {
            "nocovered": [  
                33,
                67,
                69,
                71,
                72
            ],
            "partiallycovered": []
        },
        "branch": {
            "nocovered": [67],  
            "partiallycovered": [32] 
        }
    },
    {  # 无风险文件
        "sourcefile": "Constants.java",
        "package": "com/cicc/ut/constants",
        "lines": {
            "nocovered": [],
            "partiallycovered": []
        },
        "branch": {
            "nocovered": [],
            "partiallycovered": []
        }
    },
    {  # 无风险文件
        "sourcefile": "AuthException.java",
        "package": "com/cicc/ut/exceptions",
        "lines": {
            "nocovered": [],
            "partiallycovered": []
        },
        "branch": {
            "nocovered": [],
            "partiallycovered": []
        }
    },
    {  # 无风险文件
        "sourcefile": "UserService.java",
        "package": "com/cicc/ut/service",
        "lines": {
            "nocovered": [],
            "partiallycovered": []
        },
        "branch": {
            "nocovered": [],
            "partiallycovered": []
        }
    }
]

# --- Initial Generation Function ---
# 生成初始或迭代测试计划：基于变更日志，输出JSON结构化计划
def generate_test_plan(change_log: str, feedback=None, model="gpt-oss:120b-cloud") -> dict:
    """
    生成回归测试计划。
    :param change_log: 变更日志字符串，提供变更上下文
    :param feedback: 上轮评估反馈（可选），用于迭代优化
    :param model: Ollama模型名，默认qwen3:4b（本地高效模型）
    :return: dict形式的测试计划JSON
    """
    # 构造基础prompt：指导LLM生成全接口回归计划，优先核心模块，指定JSON输出键
    prompt = f"/no_think Based on the following change log, generate a regression test plan. Focus on running the full interface library, prioritizing core modules. Output as JSON with keys: plan_summary, prioritized_modules, estimated_duration (in hours), expected_coverage (>90%). Change log: {change_log}"
    if feedback:  # 如果有反馈，注入prompt中，实现Reflection迭代
        prompt += f"\nIncorporate this feedback to improve: {feedback}"
    
    # 初始化Ollama LLM实例，使用指定模型进行本地推理
    llm = OllamaLLM(model=model)
    # 创建LangChain提示模板：动态注入prompt变量
    prompt_template = PromptTemplate(
        input_variables=["prompt"],  # 输入变量：prompt字符串
        template="{prompt}"  # 模板：直接使用注入的prompt
    )
    # 调用链：模板 | LLM，生成计划JSON字符串
    plan_json_str = (prompt_template | llm).invoke({"prompt": prompt}).strip()
    
    # 尝试解析LLM输出为dict（假设LLM严格输出JSON）
    try:
        plan = json.loads(plan_json_str)
    except json.JSONDecodeError:  # 兜底：如果LLM输出非JSON，回退到字符串dict
        plan = {"plan_summary": plan_json_str, "prioritized_modules": [], "estimated_duration": 24, "expected_coverage": 85}
    
    # 打印生成的计划，便于调试和日志追踪
    print(f"Generated Test Plan:\n{json.dumps(plan, indent=2)}")
    return plan  # 返回dict，便于后续评估和迭代

# --- Evaluation Function ---
# 评估测试计划：基于JaCoCo风险点，检查可行性（时长、覆盖、优先级）
def evaluate(plan: dict, jacoco_data: list) -> Evaluation:
    """
    评估回归测试计划的可行性。
    :param plan: 当前测试计划dict
    :param jacoco_data: JaCoCo数据列表，提取风险点
    :return: Evaluation模型实例，含状态、反馈、推理
    """
    print("\n--- Evaluating Test Plan ---")  # 日志：评估开始
    
    # 准备JaCoCo summary：遍历数据，提取nocovered lines，按package/sourcefile组风险
    risk_points = []  # 风险点列表：如"com/cicc/ut/service/impl.UserServiceImpl.java: lines [33,67,...]"
    total_nocovered_lines = 0  # 总未覆盖行数，用于粗估覆盖率
    for item in jacoco_data:  # 循环每个文件项
        nocovered_lines = item['lines']['nocovered']  # 获取lines.nocovered数组
        if nocovered_lines:  # 如果有未覆盖行
            total_nocovered_lines += len(nocovered_lines)  # 累加总数
            risk_points.append(f"{item['package']}.{item['sourcefile']}: lines {nocovered_lines} not covered")  # 组装风险描述
    
    # 模拟整体覆盖率：粗估公式（假设总行1000，nocovered比例；实际项目用精确metrics）
    estimated_coverage = max(0, 100 - (total_nocovered_lines / 10))  # 简单线性估算，防负值
    # 构建summary字符串：覆盖率 + 风险点，供prompt注入
    jacoco_summary = f"Estimated JaCoCo coverage: {estimated_coverage:.1f}%. Risk points: {'; '.join(risk_points) if risk_points else 'No major risks detected'}. Focus on uncovered lines in high-risk packages."
    
    # 创建评估prompt模板：指定标准（时长<24h、覆盖>90%、风险覆盖），注入plan和JaCoCo summary
    prompt_critique = PromptTemplate(
        input_variables=["plan", "jacoco_summary"],  # 输入：计划JSON + JaCoCo摘要
        template=(
            "/no_think\n"  # Ollama指令：无思考，直接输出
            "Critique the following regression test plan based on feasibility criteria: estimated duration reasonable (<24 hours ideal), coverage target >90%, prioritization covers high-risk modules from JaCoCo data. "  # 评估标准描述
            f"JaCoCo data: {jacoco_summary}\n"  # 注入JaCoCo摘要
            "Test Plan:\n"  # 计划输入
            "{plan}\n"  # 动态注入plan JSON
            "Respond with PASS or FAIL. Provide feedback on improvements (e.g., adjust duration, add cases for missed lines). "  # 指导输出
            "Please respond in the following JSON format:\n"  # 指定JSON结构
            "{{\"evaluation\": \"PASS|FAIL\", \"feedback\": \"...\",\"reasoning\": \"...\"}}"  # 精确格式
        )
    )
    
    # 初始化评估LLM
    llm = OllamaLLM(model="gpt-oss:120b-cloud")
    # 调用链：生成批判响应文本
    response_critique_txt = (prompt_critique | llm).invoke({"plan": json.dumps(plan), "jacoco_summary": jacoco_summary})
    
    # 使用SuperJSON解析LLM文本输出为dict（容忍非标准JSON）
    response_critique_json = SuperJSON.loads(response_critique_txt)
    # 实例化Evaluation模型，进行验证
    critique = Evaluation(**response_critique_json)
    
    # 打印评估结果，便于日志和调试
    print(f"Evaluation Status: {critique.evaluation}")
    print(f"Evaluation Feedback: {critique.feedback}")
    return critique  # 返回结构化评估结果

# Reflection Loop：核心闭环，实现生成-评估-迭代，直到PASS或max_iterations
max_iterations = 3  # 最大迭代轮次：防无限循环，平衡质量与成本（Token/时间）
current_iteration = 0  # 当前迭代计数器
# 初始计划生成：无反馈，模拟可能不通过的粗放版
current_plan = generate_test_plan(CHANGE_LOG)  # 第一轮调用，启动循环

# 主循环：Reflection自省过程
while current_iteration < max_iterations:
    current_iteration += 1  # 递增迭代计数
    print(f"\n--- Iteration {current_iteration} ---")  # 日志：当前轮次
    
    # 执行评估：注入当前计划和JaCoCo数据
    evaluation_result = evaluate(current_plan, JACOCO_DATA)
    
    # 决策分岔：PASS则收官，FAIL则反馈迭代
    if evaluation_result.evaluation == EvaluationStatus.PASS:
        print("\nFinal Test Plan:")  # 日志：最终计划
        print(json.dumps(current_plan, indent=2))  # 打印精炼计划
        break  # 退出循环：成功收尾
    else:
        # 迭代生成：用反馈优化下一版计划
        current_plan = generate_test_plan(CHANGE_LOG, feedback=evaluation_result.feedback)
        # 检查是否达max：如果是，打印最后尝试（非强制PASS）
        if current_iteration == max_iterations:
            print("\nMax iterations reached. Last attempt:")  # 日志：上限警告
            print(json.dumps(current_plan, indent=2))  # 输出最终尝试版