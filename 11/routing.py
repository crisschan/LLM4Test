import os  # 用于环境交互，如加载模拟数据（实际可扩展到MCP Server）
from super_json import SuperJSON  # 容错JSON解析：处理LLM杂质输出
from pydantic import BaseModel  # 数据验证：确保路由决策结构化
import enum  # 枚举：定义bug类别
from langchain_ollama import OllamaLLM  # LangChain Ollama集成：本地LLM调用
from langchain.prompts import PromptTemplate  # 提示模板：动态prompt
model_name = "gpt-oss:120b-cloud"
# 初始化LLM
llm = OllamaLLM(model=model_name)  # 主路由/复杂处理
llm_ui = OllamaLLM(model=model_name)  # UI专精（轻量，速答）
llm_api = OllamaLLM(model=model_name)  # API专精
llm_perf = OllamaLLM(model=model_name)  # 性能专精

# 定义路由类别枚举：测试bug分类
class Category(enum.Enum):
    UI = "ui"  # UI问题：如元素卡顿、布局崩
    API = "api"  # API问题：如OAuth失败、接口漏
    PERFORMANCE = "performance"  # 性能问题：如QPS低、DB锁
    UNKNOWN = "unknown"  # 不明：需重试或人工

# 定义路由决策模型：分类 + 推理，确保JSON严格
class RoutingDecision(BaseModel):
    category: Category  # 分类结果
    reasoning: str  # 分类依据：e.g., "关键词'卡顿'指向UI渲染"

# Step 1: Route the Bug Ticket (路由LLM - 智能分诊)
prompt_router = PromptTemplate(
    input_variables=["query"],  # 输入：bug描述
    template=(
        "/no_think Analyze the bug ticket below and determine its category.\n"
        "Categories:\n"
        "- ui: For UI/Frontend issues (e.g., rendering lag, element mismatch).\n"
        "- api: For API/Backend issues (e.g., auth failure, endpoint errors).\n"
        "- performance: For performance/scalability issues (e.g., slow load, high latency).\n"
        "- unknown: If unclear or multi-category.\n\n"
        "Bug Ticket: {query}\n"
        "Respond STRICTLY in JSON: {{\"category\": \"ui|api|performance|unknown\", \"reasoning\": \"...\"}}"
    )
)

# 示例bug票：实际从Jira/GitHub拉取
user_query = "App login is lagging with OAuth failure and high CPU usage during peak hours."  # 混杂票：UI+API+Perf
response_txt = (prompt_router | llm).invoke({"query": user_query})  # 路由调用
response_json = SuperJSON.loads(response_txt)  # 容错解析
routing_decision = RoutingDecision(**response_json)  # 模型验证
print(f"Routing Decision: {routing_decision}")  # 日志：分类结果

# Step 2: Handoff based on Routing (下游分流执行)
final_response = ""  # 最终诊断报告
if routing_decision.category == Category.UI:
    # UI专精：生成Playwright诊断+修复
    ui_prompt = PromptTemplate(
        input_variables=["query"],
        template=(
            "/no_think For UI bug '{query}': Provide diagnosis, Playwright script snippet, and fix recommendation. Output JSON: {{\"diagnosis\": \"...\", \"script_snippet\": \"...\", \"fix\": \"...\"}}"
        )
    )
    ui_txt = (ui_prompt | llm_ui).invoke({"query": user_query})
    final_response = ui_txt
    print(f"UI Diagnosis:\n{ui_txt}")

elif routing_decision.category == Category.API:
    # API专精：生成JaCoCo补案+接口测试
    api_prompt = PromptTemplate(
        input_variables=["query"],
        template=(
            "/no_think For API bug '{query}': Provide root cause, JaCoCo uncovered lines suggestion, and Pytest case. Output JSON: {{\"root_cause\": \"...\", \"jacoco_suggestion\": \"...\", \"pytests_case\": \"...\"}}"
        )
    )
    api_txt = (api_prompt | llm_api).invoke({"query": user_query})
    final_response = api_txt
    print(f"API Diagnosis:\n{api_txt}")

elif routing_decision.category == Category.PERFORMANCE:
    # 性能专精：生成JMeter调优+瓶颈分析
    perf_prompt = PromptTemplate(
        input_variables=["query"],
        template=(
            "/no_think For performance bug '{query}': Provide bottleneck analysis, JMeter config snippet, and mitigation (e.g., caching). Output JSON: {{\"bottleneck\": \"...\", \"jmeter_config\": \"...\", \"mitigation\": \"...\"}}"
        )
    )
    perf_txt = (perf_prompt | llm_perf).invoke({"query": user_query})
    final_response = perf_txt
    print(f"Performance Diagnosis:\n{perf_txt}")

else:
    # Unknown兜底：友好重试+人工建议
    unknown_prompt = PromptTemplate(
        input_variables=["query", "reasoning"],
        template=(
            "/no_think The bug ticket '{query}' is unclear. Reasoning: {reasoning}. Provide helpful rephrasing suggestions and escalate to manual review. Output JSON: {{\"suggestions\": [...], \"escalation\": \"Contact QA lead\"}}"
        )
    )
    unknown_txt = (unknown_prompt | llm).invoke({"query": user_query, "reasoning": routing_decision.reasoning})
    final_response = unknown_txt
    print(f"Unknown Handling:\n{unknown_txt}")

print(f"\nFinal Bug Diagnosis Report:\n{final_response}")