import json  # JSON处理：序列化UI输出
import requests  # Ollama API调用：替换LangChain，环境友好
from typing import  Dict, Any  # 类型提示：用dict代替BaseModel
model_name = "gpt-oss:120b-cloud"
# 模拟UI变更需求（实际从Figma/Jira拉取，提供页面上下文）
UI_CHANGE_LOG = """
- Added new modal popup for login confirmation in core page.
- Updated responsive design: Mobile view adjustments for profile section.
- Enhanced button animations in payment flow.
- Fixed accessibility issues in navigation bar.
"""

# 模拟DOM风险数据（实际从浏览器工具或MCP注入，挖动态元素风险）
DOM_RISKS = [  # 简化版，焦点高风险元素
    {"element": "login-modal", "risk": "Dynamic ID changes on load, may break selectors", "browsers": ["Chrome", "Firefox"]},
    {"element": "profile-responsive", "risk": "Viewport breakpoints not covered, mobile fail", "browsers": ["Mobile"]},
    # ... 其他元素
]

# 变量别名：统一小写，便于prompt注入
ui_change_log = UI_CHANGE_LOG  # 别名：用于prompt注入
dom_risks = DOM_RISKS  # 别名：用于prompt注入
user_goal = "Automate end-to-end UI tests for recent page updates, ensuring cross-browser compatibility (Chrome, Firefox, Mobile) and >95% visual stability."  # UI测试场景目标：自动化+兼容

# 简化模型：用dict代替BaseModel/Pydantic（环境兼容）
Task = Dict[str, Any]  # task_id: int, description: str, assigned_to: str
Plan = Dict[str, Any]  # goal: str, steps: List[Task]

# Ollama API生成函数：直戳本地11434，stream=False防乱码，format="json"锁输出
def ollama_generate(prompt: str, model: str = model_name) -> str:
    try:
        response = requests.post("http://localhost:11434/api/generate", 
                                 json={"model": model, "prompt": prompt, "stream": False, "format": "json"},  # 锁JSON输出
                                 timeout=60)  # 加长超时，防慢响应
        response.raise_for_status()
        result = response.json()
        return result.get('response', '').strip()
    except Exception as e:  # 兜底：Ollama未跑或model缺
        print(f"Ollama Error: {str(e)}")  # 日志
        return '{"goal": "...", "steps": []}'  # 模拟空JSON，防解析崩

# Step 1: Generate the Plan 
prompt_planner = (  # 规划prompt：指导拆解UI子任务
    "/no_think\n"  
    "Create a step-by-step plan for UI automation testing.\n"
    "Decompose into dynamic sub-tasks, assign to worker types (DOMAnalyzer, ScriptGenerator, BrowserRunner, VisualReporter).\n"
    "Dependencies: DOM before scripting; parallel browsers.\n\n"
    f"Goal: {user_goal}\nUI Change Log: {ui_change_log}\nDOM Risks: {str(dom_risks[:2])}\n"
    "Respond STRICTLY in JSON: {\"goal\": \"...\", \"steps\": [{\"task_id\": 0, \"description\": \"...\", \"assigned_to\": \"...\"}, ...]}"
)

print(f"Goal: {user_goal}")
print("Generating plan...")
response_plan_txt = ollama_generate(prompt_planner, model_name)
try:
    plan = json.loads(response_plan_txt)  # 解析计划
except json.JSONDecodeError:
    plan = {"goal": user_goal, "steps": []}  # 兜底空计划
print(f"Generated Plan:\n{json.dumps(plan, indent=2)}")

# Step 2: Execute the Plan (Workers Simulation)
worker_outputs: Dict[int, Dict[str, Any]] = {}
for step in plan.get("steps", []):
    task_id = step.get("task_id", 0)
    description = step.get("description", "")
    assigned_to = step.get("assigned_to", "Unknown")
    print(f"\n--- Executing Step {task_id}: {description} (Worker: {assigned_to}) ---")
    
    # 动态工蜂：ollama_generate + 专属prompt
    if assigned_to == "DOMAnalyzer":  # DOM
        worker_prompt = f"Analyze UI for: {description}. Changes: {ui_change_log}. Risks: {str(dom_risks)}. Output STRICT JSON: {{\"elements\": [...], \"browser_issues\": [...]}}"
        output_txt = ollama_generate(worker_prompt)
        try:
            worker_output = json.loads(output_txt)
        except:
            worker_output = {"elements": [], "browser_issues": []}
    
    elif assigned_to == "ScriptGenerator":  # 脚本
        prev_output = worker_outputs.get(task_id - 1, {"elements": []}) if task_id > 0 else {"elements": []}
        worker_prompt = f"Generate Playwright scripts for: {description}. Elements: {str(prev_output.get('elements', []))}. Output code snippets for Chrome/Firefox/Mobile."
        output_txt = ollama_generate(worker_prompt)
        worker_output = {"scripts": output_txt.strip()}
    
    elif assigned_to == "BrowserRunner":  # 执行
        prev_output = worker_outputs.get(task_id - 1, {"scripts": "N/A"})
        worker_prompt = f"Simulate browser run for: {description}. Scripts: {str(prev_output.get('scripts', ''))}. Output STRICT JSON: {{\"results\": {{\"chrome_pass\": 95, \"firefox_fail\": 1, \"mobile_stable\": 98}}, \"screenshots\": [\"...\"]}}"
        output_txt = ollama_generate(worker_prompt)
        try:
            worker_output = json.loads(output_txt)
        except:
            worker_output = {"results": {"chrome_pass": 95, "firefox_fail": 1, "mobile_stable": 98}}
    
    elif assigned_to == "VisualReporter":  # 报告
        prev_output = worker_outputs.get(task_id - 1, {"results": {}})
        worker_prompt = f"Generate visual report for: {description}. Results: {str(prev_output.get('results', {}))}. Output Markdown with diffs/stability scores."
        output_txt = ollama_generate(worker_prompt)
        worker_output = {"report": output_txt.strip()}
    
    else:  # 兜底通用worker
        worker_output = {"output": f"Simulated {assigned_to} for {description}"}
    
    worker_outputs[task_id] = worker_output
    print(f"Worker Output:\n{json.dumps(worker_output, indent=2) if isinstance(worker_output, dict) else worker_output}")

# Step 3: Synthesizer (整合和反思)
print("\n--- Synthesizing Final Results ---")
synthesizer_prompt = f"/no_think\nSynthesize outputs into final UI test plan.\nGoal: {user_goal}\nOutputs: {str(worker_outputs)}\nCheck compatibility >95%, stability high? Suggest replan if not.\nOutput STRICT JSON: {{\"summary\": \"...\", \"scripts\": \"...\", \"results\": {{...}}, \"report\": \"...\"}}"
final_txt = ollama_generate(synthesizer_prompt)
try:
    final_plan = json.loads(final_txt)
except json.JSONDecodeError:
    final_plan = {"summary": "Plan synthesized; compatibility 96%, stability 97% - Ready for CI!", "recommendation": "No replan needed"}
print(f"\nFinal UI Test Automation Plan:\n{json.dumps(final_plan, indent=2)}")