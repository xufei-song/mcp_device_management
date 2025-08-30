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


def run_with_fastapi():
    """使用FastAPI运行MCP服务器"""
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    import json
    
    logger.info("创建FastAPI MCP服务器 - HTTP JSON-RPC模式")
    
    # 创建FastAPI应用
    fastapi_app = FastAPI(
        title="测试设备管理MCP服务器",
        description="基于官方MCP Python SDK的HTTP JSON-RPC服务器",
        version="1.0.0"
    )
    
    # 添加中间件记录所有请求
    @fastapi_app.middleware("http")
    async def log_requests(request, call_next):
        logger.info(f"收到请求: {request.method} {request.url}")
        logger.info(f"Headers: {dict(request.headers)}")
        
        # 对于POST请求，尝试记录请求体
        if request.method == "POST":
            try:
                # 读取请求体但不消费stream
                body = await request.body()
                if body:
                    import json
                    try:
                        body_json = json.loads(body.decode())
                        logger.info(f"请求体: {body_json}")
                    except:
                        logger.info(f"请求体(非JSON): {body[:200]}...")
            except Exception as e:
                logger.debug(f"无法读取请求体: {e}")
        
        response = await call_next(request)
        logger.info(f"响应状态: {response.status_code}")
        return response
    
    @fastapi_app.post("/mcp")
    async def mcp_post_handler(request_data: dict):
        """处理MCP POST请求 - 实现完整的JSON-RPC 2.0协议"""
        logger.info(f"收到MCP POST请求: {request_data}")
        
        try:
            method = request_data.get("method")
            params = request_data.get("params", {})
            request_id = request_data.get("id")
            
            logger.info(f"处理方法: {method}, 参数: {params}")
            
            if method == "initialize":
                # 初始化响应 - 参考成功的fastmcp_test_server实现
                result = {
                    "protocolVersion": "2024-11-05",  # 使用与成功服务器相同的版本
                    "capabilities": {
                        "tools": {},  # 空对象表示支持工具
                        "prompts": {}  # 空对象表示支持提示
                    },
                    "serverInfo": {
                        "name": "TestDeviceManagement",
                        "version": "1.0.0"
                    }
                }
                logger.info(f"初始化成功，返回完整能力信息")
                # 修复日志显示 - 应该检查是否为字典而不是bool
                tools_supported = 'tools' in result['capabilities'] and result['capabilities']['tools'] is not None
                prompts_supported = 'prompts' in result['capabilities'] and result['capabilities']['prompts'] is not None
                logger.info(f"服务器能力: tools={tools_supported}, prompts={prompts_supported}")
                
            elif method == "tools/list":
                # 返回工具列表
                tools = await handle_list_tools()
                # 将Tool对象转换为字典
                tools_dict = []
                for tool in tools:
                    tool_dict = {
                        "name": tool.name,
                        "description": tool.description,
                        "inputSchema": tool.inputSchema
                    }
                    tools_dict.append(tool_dict)
                result = {"tools": tools_dict}
                logger.info(f"返回工具列表: {len(tools)}个工具")
                
            elif method == "tools/call":
                # 调用工具
                tool_name = params.get("name")
                tool_arguments = params.get("arguments", {})
                content_list = await handle_call_tool(tool_name, tool_arguments)
                # 将TextContent对象转换为字典
                content_dict = []
                for content in content_list:
                    # 安全地获取文本内容
                    text_content = getattr(content, 'text', str(content))
                    content_dict.append({
                        "type": "text",
                        "text": text_content
                    })
                result = {
                    "content": content_dict,
                    "isError": False
                }
                logger.info(f"工具调用完成: {tool_name}")
                
            elif method == "prompts/list":
                # 返回提示列表
                prompts = await handle_list_prompts()
                # 将Prompt对象转换为字典
                prompts_dict = []
                for prompt in prompts:
                    prompt_dict = {
                        "name": prompt.name,
                        "description": prompt.description,
                        "arguments": [
                            {
                                "name": arg.name,
                                "description": arg.description,
                                "required": arg.required
                            } for arg in (prompt.arguments or [])
                        ]
                    }
                    prompts_dict.append(prompt_dict)
                result = {"prompts": prompts_dict}
                logger.info(f"返回提示列表: {len(prompts)}个提示")
                
            elif method == "prompts/get":
                # 获取提示
                prompt_name = params.get("name")
                prompt_arguments = params.get("arguments", {})
                prompt_result = await handle_get_prompt(prompt_name, prompt_arguments)
                # 将GetPromptResult对象转换为字典
                messages_dict = []
                for msg in prompt_result.messages:
                    # 安全地获取消息内容
                    text_content = getattr(msg.content, 'text', str(msg.content))
                    content_dict = {
                        "type": "text",
                        "text": text_content
                    }
                    messages_dict.append({
                        "role": msg.role,
                        "content": content_dict
                    })
                
                result = {
                    "description": prompt_result.description,
                    "messages": messages_dict
                }
                logger.info(f"提示获取完成: {prompt_name}")
                
            elif method == "notifications/initialized":
                # 处理初始化通知 - 这是一个通知，不需要响应
                logger.info("收到初始化完成通知")
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {}  # 返回空结果表示收到通知
                })
                
            else:
                logger.warning(f"未知方法: {method}")
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"未知方法: {method}"
                    }
                })
            
            # 返回成功响应，包含适当的头部
            response = JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            })
            
            # 添加必要的头部以支持长连接
            response.headers["Connection"] = "keep-alive"
            response.headers["Cache-Control"] = "no-cache"
            
            logger.info(f"成功处理{method}请求，返回结果")
            logger.debug(f"响应内容: {result}")
            return response
            
        except Exception as e:
            logger.error(f"处理MCP POST请求失败: {e}")
            import traceback
            traceback.print_exc()
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_data.get("id"),
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            })
    
    @fastapi_app.get("/mcp")
    async def mcp_stream_handler():
        """处理MCP GET请求 - 建立双向HTTP Stream连接"""
        logger.info("收到MCP GET请求 - 建立HTTP Stream连接")
        
        from fastapi.responses import StreamingResponse
        import json
        import asyncio
        
        async def mcp_event_stream():
            """MCP HTTP Stream事件流 - 保持连接用于服务器推送"""
            try:
                logger.info("开始MCP事件流 - 仅用于保持连接")
                
                # 根据官方文档，HTTP Stream主要用于保持连接
                # 实际的工具和提示列表应该通过POST请求获取
                
                # 发送连接建立确认
                yield f"data: {json.dumps({'type': 'connected', 'timestamp': datetime.now().isoformat()})}\n\n"
                logger.info("HTTP Stream连接已建立")
                
                # 保持连接活跃 - 定期发送心跳
                heartbeat_count = 0
                while True:
                    await asyncio.sleep(30)  # 每30秒发送心跳
                    heartbeat_count += 1
                    
                    heartbeat_msg = {
                        "type": "heartbeat",
                        "sequence": heartbeat_count,
                        "timestamp": datetime.now().isoformat(),
                        "server": "TestDeviceManagement"
                    }
                    yield f"data: {json.dumps(heartbeat_msg)}\n\n"
                    logger.debug(f"发送心跳 #{heartbeat_count}")
                    
            except asyncio.CancelledError:
                logger.info("Stream连接被客户端关闭")
                raise
            except Exception as e:
                logger.error(f"Stream连接错误: {e}")
                error_msg = {
                    "type": "error",
                    "message": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                yield f"data: {json.dumps(error_msg)}\n\n"
        
        return StreamingResponse(
            mcp_event_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Cache-Control, Content-Type",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            }
        )
    
    @fastapi_app.options("/mcp")
    async def mcp_options_handler():
        """处理MCP OPTIONS请求 - CORS预检"""
        logger.info("收到MCP OPTIONS请求")
        return JSONResponse(
            content={},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
            }
        )
    
    @fastapi_app.get("/")
    async def root():
        """根路径 - 服务器信息"""
        logger.info("收到根路径请求")
        return {
            "name": "TestDeviceManagement",
            "description": "测试设备管理MCP服务器",
            "version": "1.0.0",
            "protocol": "mcp",
            "transport": "http",
            "endpoints": {
                "mcp": "/mcp",
                "health": "/health",
                "docs": "/docs"
            },
            "tools": ["get_device_info", "list_devices"],
            "prompts": ["device_test_plan", "bug_report_template"]
        }
    
    @fastapi_app.get("/health")
    async def health_check():
        """健康检查端点"""
        logger.info("收到健康检查请求")
        
        # 测试工具和提示是否正常
        try:
            tools = await handle_list_tools()
            prompts = await handle_list_prompts()
            
            return {
                "status": "healthy", 
                "server": "TestDeviceManagement",
                "mcp": {
                    "tools_count": len(tools),
                    "prompts_count": len(prompts),
                    "capabilities": ["tools", "prompts", "http-stream"]
                },
                "endpoints": {
                    "mcp_post": "POST /mcp",
                    "mcp_stream": "GET /mcp",
                    "health": "GET /health"
                }
            }
        except Exception as e:
            logger.error(f"健康检查失败: {e}")
            return {
                "status": "error",
                "server": "TestDeviceManagement", 
                "error": str(e)
            }
    
    # 添加错误处理
    @fastapi_app.exception_handler(404)
    async def not_found_handler(request, exc):
        logger.warning(f"404错误: {request.method} {request.url}")
        return JSONResponse(
            status_code=404,
            content={
                "error": "Not Found",
                "message": f"端点 {request.url.path} 不存在",
                "available_endpoints": ["/", "/mcp", "/health", "/docs"]
            }
        )
    
    @fastapi_app.exception_handler(405)
    async def method_not_allowed_handler(request, exc):
        logger.warning(f"405错误: {request.method} {request.url}")
        return JSONResponse(
            status_code=405,
            content={
                "error": "Method Not Allowed",
                "message": f"{request.method} 方法不被支持",
                "supported_methods": ["GET", "POST", "OPTIONS"]
            }
        )
    
    return fastapi_app


if __name__ == "__main__":
    import uvicorn
    
    logger.info("启动测试设备管理MCP服务器")
    logger.info("服务器地址: http://localhost:8001")
    logger.info("MCP端点: http://localhost:8001/mcp")
    logger.info("健康检查: http://localhost:8001/health")
    
    # 创建FastAPI应用
    fastapi_app = run_with_fastapi()
    
    # 运行服务器
    uvicorn.run(
        fastapi_app,
        host="localhost", 
        port=8001,
        log_level="info"
    )