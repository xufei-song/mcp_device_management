"""
测试设备管理MCP服务器
基于官方MCP Python SDK实现的HTTP Stream MCP服务器
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence

from mcp.server import Server
from mcp.types import (
    CallToolResult,
    GetPromptResult,
    ListPromptsResult,
    ListToolsResult,
    Prompt,
    PromptArgument,
    PromptMessage,
    TextContent,
    Tool,
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("TestDeviceManagementMCP")

# 创建MCP服务器实例
app = Server("TestDeviceManagement")


@app.list_tools()
async def handle_list_tools() -> List[Tool]:
    """
    返回可用的工具列表
    """
    logger.info("处理tools/list请求")
    
    tools = [
        Tool(
            name="get_device_info",
            description="获取设备信息，包括设备状态、型号、系统版本等",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "string",
                        "description": "设备ID，如emulator-5554或device_serial_number"
                    },
                    "device_type": {
                        "type": "string",
                        "enum": ["android", "ios", "windows"],
                        "description": "设备类型"
                    }
                },
                "required": ["device_id", "device_type"]
            }
        ),
        Tool(
            name="list_devices",
            description="列出所有可用的测试设备",
            inputSchema={
                "type": "object",
                "properties": {
                    "device_type": {
                        "type": "string",
                        "enum": ["android", "ios", "windows", "all"],
                        "description": "过滤设备类型，all表示所有类型",
                        "default": "all"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["online", "offline", "all"],
                        "description": "过滤设备状态，all表示所有状态",
                        "default": "all"
                    }
                }
            }
        )
    ]
    
    logger.info(f"返回{len(tools)}个工具")
    return tools


@app.call_tool()
async def handle_call_tool(name: str, arguments: Optional[Dict[str, Any]]) -> Sequence[TextContent]:
    """
    处理工具调用请求
    """
    logger.info(f"处理工具调用: {name}, 参数: {arguments}")
    
    try:
        if name == "get_device_info":
            return await _handle_get_device_info(arguments or {})
        elif name == "list_devices":
            return await _handle_list_devices(arguments or {})
        else:
            return [TextContent(type="text", text=f"未知工具: {name}")]
            
    except Exception as e:
        logger.error(f"工具调用失败: {e}")
        return [TextContent(type="text", text=f"工具调用失败: {str(e)}")]


async def _handle_get_device_info(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """处理获取设备信息工具"""
    device_id = arguments.get("device_id")
    device_type = arguments.get("device_type")
    
    if not device_id or not device_type:
        return [TextContent(type="text", text="缺少必需参数: device_id 或 device_type")]
    
    # Mock设备信息数据
    mock_device_info = {
        "device_id": device_id,
        "device_type": device_type,
        "status": "online",
        "model": f"Mock_{device_type.upper()}_Device",
        "os_version": "Mock_OS_1.0",
        "screen_resolution": "1080x1920",
        "cpu_usage": "15%",
        "memory_usage": "60%",
        "last_update": datetime.now().isoformat(),
        "capabilities": [
            "screenshot",
            "app_install",
            "app_uninstall",
            "input_simulation",
            "log_collection"
        ]
    }
    
    result_text = f"""设备信息获取成功:
设备ID: {mock_device_info['device_id']}
设备类型: {mock_device_info['device_type']}
状态: {mock_device_info['status']}
型号: {mock_device_info['model']}
系统版本: {mock_device_info['os_version']}
屏幕分辨率: {mock_device_info['screen_resolution']}
CPU使用率: {mock_device_info['cpu_usage']}
内存使用率: {mock_device_info['memory_usage']}
最后更新: {mock_device_info['last_update']}
支持功能: {', '.join(mock_device_info['capabilities'])}
"""
    
    logger.info(f"返回设备信息: {device_id}")
    return [TextContent(type="text", text=result_text)]


async def _handle_list_devices(arguments: Dict[str, Any]) -> Sequence[TextContent]:
    """处理列出设备工具"""
    device_type = arguments.get("device_type", "all")
    status = arguments.get("status", "all")
    
    # Mock设备列表数据
    mock_devices = [
        {
            "device_id": "emulator-5554",
            "device_type": "android",
            "status": "online",
            "model": "Android_Emulator_API_34",
            "os_version": "Android 14"
        },
        {
            "device_id": "emulator-5556",
            "device_type": "android", 
            "status": "offline",
            "model": "Android_Emulator_API_33",
            "os_version": "Android 13"
        },
        {
            "device_id": "ios-simulator-1",
            "device_type": "ios",
            "status": "online",
            "model": "iPhone_15_Pro_Simulator",
            "os_version": "iOS 17.0"
        },
        {
            "device_id": "windows-vm-1",
            "device_type": "windows",
            "status": "online",
            "model": "Windows_VM",
            "os_version": "Windows 11"
        }
    ]
    
    # 按类型过滤
    if device_type != "all":
        mock_devices = [d for d in mock_devices if d["device_type"] == device_type]
    
    # 按状态过滤
    if status != "all":
        mock_devices = [d for d in mock_devices if d["status"] == status]
    
    result_text = f"设备列表 (类型: {device_type}, 状态: {status}):\n\n"
    
    for device in mock_devices:
        result_text += f"• 设备ID: {device['device_id']}\n"
        result_text += f"  类型: {device['device_type']}\n"
        result_text += f"  状态: {device['status']}\n"
        result_text += f"  型号: {device['model']}\n"
        result_text += f"  系统: {device['os_version']}\n\n"
    
    if not mock_devices:
        result_text += "未找到符合条件的设备。\n"
    else:
        result_text += f"共找到 {len(mock_devices)} 个设备。"
    
    logger.info(f"返回设备列表: {len(mock_devices)}个设备")
    return [TextContent(type="text", text=result_text)]


@app.list_prompts()
async def handle_list_prompts() -> List[Prompt]:
    """
    返回可用的提示列表
    """
    logger.info("处理prompts/list请求")
    
    prompts = [
        Prompt(
            name="device_test_plan",
            description="生成设备测试计划模板",
            arguments=[
                PromptArgument(
                    name="device_type",
                    description="设备类型 (android/ios/windows)",
                    required=True
                ),
                PromptArgument(
                    name="test_scope",
                    description="测试范围 (功能测试/性能测试/兼容性测试)",
                    required=False
                )
            ]
        ),
        Prompt(
            name="bug_report_template",
            description="生成Bug报告模板",
            arguments=[
                PromptArgument(
                    name="device_id",
                    description="出现问题的设备ID",
                    required=True
                ),
                PromptArgument(
                    name="severity",
                    description="问题严重程度 (低/中/高/紧急)",
                    required=False
                )
            ]
        )
    ]
    
    logger.info(f"返回{len(prompts)}个提示")
    return prompts


@app.get_prompt()
async def handle_get_prompt(name: str, arguments: Optional[Dict[str, str]]) -> GetPromptResult:
    """
    处理获取提示请求
    """
    logger.info(f"处理提示获取: {name}, 参数: {arguments}")
    
    try:
        if name == "device_test_plan":
            return await _handle_device_test_plan_prompt(arguments or {})
        elif name == "bug_report_template":
            return await _handle_bug_report_template_prompt(arguments or {})
        else:
            # 返回错误提示
            return GetPromptResult(
                description=f"未知提示: {name}",
                messages=[
                    PromptMessage(
                        role="user",
                        content=TextContent(type="text", text=f"错误：未找到名为 '{name}' 的提示模板")
                    )
                ]
            )
            
    except Exception as e:
        logger.error(f"提示处理失败: {e}")
        return GetPromptResult(
            description=f"提示处理失败",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=f"处理提示时发生错误: {str(e)}")
                )
            ]
        )


async def _handle_device_test_plan_prompt(arguments: Dict[str, str]) -> GetPromptResult:
    """处理设备测试计划提示"""
    device_type = arguments.get("device_type", "通用")
    test_scope = arguments.get("test_scope", "功能测试")
    
    prompt_content = f"""
# {device_type.upper()} 设备测试计划

## 测试范围: {test_scope}

## 测试环境
- 设备类型: {device_type}
- 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 测试用例

### 1. 基础功能测试
- [ ] 设备连接测试
- [ ] 设备信息获取
- [ ] 屏幕截图功能
- [ ] 应用安装/卸载

### 2. 性能测试
- [ ] CPU使用率监控
- [ ] 内存使用率监控
- [ ] 网络连接测试
- [ ] 电池消耗测试

### 3. 兼容性测试
- [ ] 不同版本系统测试
- [ ] 不同分辨率适配
- [ ] 多设备并发测试

## 预期结果
所有测试用例都应该通过，设备应该保持稳定运行状态。

## 注意事项
- 测试前确保设备已正确连接
- 记录所有异常情况和错误日志
- 测试完成后生成详细报告
"""
    
    return GetPromptResult(
        description="设备测试计划",
        messages=[
            PromptMessage(
                role="user",
                content=TextContent(type="text", text=prompt_content)
            )
        ]
    )


async def _handle_bug_report_template_prompt(arguments: Dict[str, str]) -> GetPromptResult:
    """处理Bug报告模板提示"""
    device_id = arguments.get("device_id", "未指定")
    severity = arguments.get("severity", "中")
    
    prompt_content = f"""
# Bug报告

## 基本信息
- 报告时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- 设备ID: {device_id}
- 严重程度: {severity}
- 报告人: [请填写]

## 问题描述
[请详细描述遇到的问题]

## 复现步骤
1. [步骤1]
2. [步骤2]
3. [步骤3]

## 预期结果
[描述期望的正确行为]

## 实际结果
[描述实际发生的错误行为]

## 环境信息
- 设备型号: [请填写]
- 系统版本: [请填写]
- 应用版本: [请填写]

## 附加信息
- 错误日志: [如有请附上]
- 截图/视频: [如有请附上]
- 其他相关信息: [请补充]

## 影响范围
[描述此问题可能影响的功能或用户]

## 解决方案建议
[如有解决方案建议请填写]
"""
    
    return GetPromptResult(
        description="Bug报告模板",
        messages=[
            PromptMessage(
                role="user",
                content=TextContent(type="text", text=prompt_content)
            )
        ]
    )


def create_http_server():
    """
    创建HTTP服务器实例
    """
    logger.info("创建HTTP MCP服务器")
    return app


def create_simple_http_server():
    """创建简单的HTTP服务器，包装MCP Server对象"""
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    import json
    
    logger.info("创建简化的HTTP MCP服务器，参考成功实现")
    
    # 创建FastAPI应用
    fastapi_app = FastAPI(
        title="测试设备管理MCP服务器", 
        description="简化HTTP实现，专注工具和提示功能",
        version="1.0.0"
    )
    
    @fastapi_app.post("/mcp")
    async def handle_mcp_request(request_data: dict):
        """处理MCP请求 - 参考fastmcp_test_server的成功实现"""
        try:
            logger.info(f"[MCP] 收到请求: {request_data}")
            
            method = request_data.get("method")
            params = request_data.get("params", {})
            request_id = request_data.get("id")
            
            if method == "initialize":
                response = {
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {},
                            "prompts": {}
                        },
                        "serverInfo": {
                            "name": "TestDeviceManagement",
                            "version": "1.0.0"
                        }
                    }
                }
            elif method == "tools/list":
                tools = await handle_list_tools()
                tools_list = []
                for tool in tools:
                    tools_list.append({
                        "name": tool.name,
                        "description": tool.description,
                        "inputSchema": tool.inputSchema
                    })
                response = {"result": {"tools": tools_list}}
                
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                content_list = await handle_call_tool(tool_name, arguments)
                
                # 转换为简单的文本结果
                text_result = ""
                for content in content_list:
                    text_result += getattr(content, 'text', str(content))
                
                response = {
                    "result": {
                        "content": [
                            {
                                "type": "text", 
                                "text": text_result
                            }
                        ]
                    }
                }
                
            elif method == "prompts/list":
                prompts = await handle_list_prompts()
                prompts_list = []
                for prompt in prompts:
                    prompts_list.append({
                        "name": prompt.name,
                        "description": prompt.description,
                        "arguments": [
                            {
                                "name": arg.name,
                                "description": arg.description,
                                "required": arg.required
                            } for arg in (prompt.arguments or [])
                        ]
                    })
                response = {"result": {"prompts": prompts_list}}
                
            elif method == "prompts/get":
                prompt_name = params.get("name")
                arguments = params.get("arguments", {})
                prompt_result = await handle_get_prompt(prompt_name, arguments)
                
                response = {
                    "result": {
                        "description": prompt_result.description,
                        "messages": [
                            {
                                "role": msg.role,
                                "content": {
                                    "type": "text",
                                    "text": getattr(msg.content, 'text', str(msg.content))
                                }
                            } for msg in prompt_result.messages
                        ]
                    }
                }
                
            else:
                response = {
                    "error": {
                        "code": -32601,
                        "message": f"未知方法: {method}"
                    }
                }
            
            result = {
                "jsonrpc": "2.0",
                "id": request_id,
                **response
            }
            
            logger.info(f"[MCP] 发送响应: {result}")
            return JSONResponse(content=result)
            
        except Exception as e:
            logger.error(f"[MCP] 处理请求时出错: {str(e)}")
            error_response = {
                "jsonrpc": "2.0",
                "id": request_data.get("id") if 'request_data' in locals() else None,
                "error": {
                    "code": -32603,
                    "message": f"内部服务器错误: {str(e)}"
                }
            }
            return JSONResponse(content=error_response, status_code=500)
    
    @fastapi_app.get("/health")
    async def health_check():
        """健康检查"""
        try:
            tools = await handle_list_tools()
            prompts = await handle_list_prompts()
            return {
                "status": "healthy",
                "server": "TestDeviceManagement",
                "tools_count": len(tools),
                "prompts_count": len(prompts)
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    return fastapi_app


if __name__ == "__main__":
    import uvicorn
    
    logger.info("启动测试设备管理MCP服务器")
    logger.info("服务器地址: http://localhost:8001")
    logger.info("MCP端点: http://localhost:8001/mcp")
    logger.info("健康检查: http://localhost:8001/health")
    
    # 创建FastAPI应用
    fastapi_app = create_simple_http_server()
    
    # 运行服务器
    uvicorn.run(
        fastapi_app,
        host="localhost", 
        port=8001,
        log_level="info"
    )