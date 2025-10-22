from mcp.server import FastMCP # 导入 FastMCP 库（MCP 的快速开发工具）

mcp = FastMCP("Demo")# 这个Demo就是MCP Server的名字

@mcp.resource(  # 装饰器：注册一个静态资源（固定 URI，不带参数）
    uri="file:///project/README.md",  # 资源的"地址"：本地文件路径，file:/// 是标准协议
    title="项目 README",  # 标题：人话描述，AI list 时显示
    description="功能概述",  # 描述：告诉 AI 这个资源是干啥的（电商项目概述）
    mime_type="text/markdown"  # 文件类型：Markdown 文本，AI 知道怎么解析（e.g., 渲染成 HTML）
)

def get_readme():# 绑定的函数：Server 收到 read 请求时执行这个
    with open("project/README.md", "r", encoding="utf-8") as f:  # 打开本地文件，指定UTF-8编码
        return f.read()  # 返回文件内容（纯文本），Server 自动包成 MCP 响应


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')