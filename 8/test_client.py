#!/usr/bin/env python3
"""
简单的MCP客户端测试脚本
"""
import asyncio
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_connection():
    """测试MCP服务器连接"""
    print("🚀 启动MCP客户端测试...")
    
    # 创建服务器参数
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "python", "mcp_server_tool.py"],
        env=None
    )
    
    try:
        print("📡 连接到MCP服务器...")
        async with stdio_client(server_params) as (read, write):
            print("✅ 连接成功")
            
            async with ClientSession(read, write) as session:
                print("🔧 初始化会话...")
                await session.initialize()
                print("✅ 会话初始化成功")
                
                # 列出可用工具
                print("📋 获取可用工具...")
                tools = await session.list_tools()
                print(f"✅ 找到 {len(tools.tools)} 个工具:")
                for tool in tools.tools:
                    print(f"  - {tool.name}: {tool.description}")
                
                # 测试工具调用
                if tools.tools:
                    tool_name = tools.tools[0].name
                    print(f"🧪 测试工具: {tool_name}")
                    
                    if tool_name == "add":
                        result = await session.call_tool("add", {"a": 5, "b": 3})
                        print(f"✅ 工具调用成功: 5 + 3 = {result}")
                    else:
                        print(f"⚠️  未知工具: {tool_name}")
                
                print("🎉 测试完成!")
                
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_connection())
    sys.exit(0 if success else 1)
