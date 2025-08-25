"""
MCP Streamable HTTP 服务器测试客户端
"""

import asyncio
import json
import aiohttp
import uuid
from typing import Dict, Any

class MCPTestClient:
    """MCP 测试客户端"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.session_id = None
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def send_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """发送 MCP 请求"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "MCP-Protocol-Version": "2025-06-18"
        }
        
        if self.session_id:
            headers["MCP-Session-Id"] = self.session_id
        
        request_data = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": method
        }
        
        if params:
            request_data["params"] = params
        
        print(f"发送请求: {json.dumps(request_data, ensure_ascii=False, indent=2)}")
        
        async with self.session.post(
            f"{self.base_url}/mcp",
            headers=headers,
            json=request_data
        ) as response:
            result = await response.json()
            print(f"收到响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
            # 保存会话ID
            if "mcp-session-id" in response.headers:
                self.session_id = response.headers["mcp-session-id"]
                print(f"会话ID: {self.session_id}")
            
            return result
    
    async def initialize(self) -> Dict[str, Any]:
        """初始化连接"""
        return await self.send_request("initialize", {
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": {
                "name": "MCPTestClient",
                "version": "1.0.0"
            }
        })
    
    async def list_tools(self) -> Dict[str, Any]:
        """获取工具列表"""
        return await self.send_request("tools/list")
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """调用工具"""
        return await self.send_request("tools/call", {
            "name": name,
            "arguments": arguments
        })
    
    async def list_prompts(self) -> Dict[str, Any]:
        """获取提示列表"""
        return await self.send_request("prompts/list")

async def test_mcp_server():
    """测试 MCP 服务器"""
    print("开始测试 MCP Streamable HTTP 服务器...")
    
    async with MCPTestClient() as client:
        # 1. 初始化
        print("\n=== 1. 初始化 ===")
        init_result = await client.initialize()
        print(f"初始化结果: {init_result.get('result', {}).get('serverInfo', {})}")
        
        # 2. 获取工具列表
        print("\n=== 2. 获取工具列表 ===")
        tools_result = await client.list_tools()
        tools = tools_result.get('result', {}).get('tools', [])
        print(f"可用工具数量: {len(tools)}")
        for tool in tools:
            print(f"  - {tool['name']}: {tool['description']}")
        
        # 3. 调用工具1
        print("\n=== 3. 调用工具1 ===")
        tool1_result = await client.call_tool("simple_tool_1", {
            "message": "你好，这是测试消息"
        })
        content = tool1_result.get('result', {}).get('content', [])
        if content:
            print(f"工具1结果: {content[0].get('text', '')}")
        
        # 4. 调用工具2
        print("\n=== 4. 调用工具2 ===")
        tool2_result = await client.call_tool("simple_tool_2", {
            "number": 5
        })
        content = tool2_result.get('result', {}).get('content', [])
        if content:
            print(f"工具2结果: {content[0].get('text', '')}")
        
        # 5. 获取提示列表
        print("\n=== 5. 获取提示列表 ===")
        prompts_result = await client.list_prompts()
        prompts = prompts_result.get('result', {}).get('prompts', [])
        print(f"可用提示数量: {len(prompts)}")
        for prompt in prompts:
            print(f"  - {prompt['name']}: {prompt['description']}")
        
        # 6. 测试错误情况
        print("\n=== 6. 测试错误情况 ===")
        error_result = await client.call_tool("unknown_tool", {})
        if 'error' in error_result:
            print(f"错误测试成功: {error_result['error']['message']}")

if __name__ == "__main__":
    asyncio.run(test_mcp_server())
