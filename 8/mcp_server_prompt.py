from mcp.server import FastMCP  # 导入 FastMCP 库（MCP 的快速开发工具）
mcp = FastMCP("Demo")  # 创建 MCP Server 实例，名字 "Demo"
@mcp.prompt(  # 装饰器：注册 Prompt
    name="testcase_gen",  # 内部 ID（小写 + 下划线规范）
    title="边界值测试用例生成器",  # 新增：UI 短标题
    description="根据输入的需求描述，采用边界值分析法设计测试用例（覆盖正常/边界/异常输入）"  # 优化描述：更精确
)
def testcase_gen(message: str) -> list:  # 改返回：list of dicts（消息列表）
    return [  # 标准 messages 结构：system + user
        {  # System 消息：设角色 + 规则（隐形导演）
            "role": "system",
            "content": """你是资深测试开发工程师，专精边界值分析法。
边界值原则：针对输入范围，测试 min、max、min-1、max+1、nominal（正常值）、空值/无效。
输出格式：用 Markdown 表格列出用例（ID | 输入 | 预期 | 类型：正常/边界/异常）。
保持简洁、专业，只输出用例表，无多余解释。"""
        },
        {  # User 消息：注入需求 + 引导
            "role": "user",
            "content": f"需求：{message}\n\n请基于边界值方法设计测试用例。"
        }
    ]
if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')