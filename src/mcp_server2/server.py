"""
使用官方MCP SDK StreamableHTTP实现的设备管理服务器
参考官方示例，正确使用SDK API
"""

import contextlib
import logging
import sys
from collections.abc import AsyncIterator
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import anyio
import click
import mcp.types as types
from mcp.server.lowlevel import Server
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.routing import Mount
from starlette.types import Receive, Scope, Send

from .event_store import InMemoryEventStore

# 导入device模块
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.append(str(project_root))

from src.device.android_reader import read_android_devices
from src.device.ios_reader import read_ios_devices
from src.device.windows_reader import read_windows_devices, get_all_architectures, query_devices_by_architecture
from src.device.other_reader import read_other_devices
from src.device.records_reader import read_records

# 配置日志
logger = logging.getLogger(__name__)


@click.command()
@click.option("--port", default=8002, help="HTTP服务器端口")
@click.option(
    "--log-level",
    default="INFO",
    help="日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
)
@click.option(
    "--json-response",
    is_flag=True,
    default=False,
    help="启用JSON响应而不是SSE流",
)
def main(
    port: int,
    log_level: str,
    json_response: bool,
) -> int:
    """启动设备管理MCP服务器"""
    # 配置日志
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    logger.info("启动设备管理MCP服务器 (使用官方SDK)")
    
    # 创建MCP服务器实例 - 使用官方SDK
    app = Server("DeviceManagement-SDK")

    @app.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[types.ContentBlock]:
        """处理工具调用 - 使用SDK标准接口"""
        ctx = app.request_context
        logger.info(f"[SDK] 工具调用: {name}, 参数: {arguments}")
        
        try:
            if name == "get_device_info":
                return await _handle_get_device_info(arguments, ctx)
            elif name == "list_devices":
                return await _handle_list_devices(arguments, ctx)
            elif name == "get_windows_architectures":
                return await _handle_get_windows_architectures(arguments, ctx)
            elif name == "query_devices_by_architecture":
                return await _handle_query_devices_by_architecture(arguments, ctx)
            elif name == "get_device_records":
                return await _handle_get_device_records(arguments, ctx)
            elif name == "send_notification_test":
                return await _handle_notification_test(arguments, ctx)
            else:
                return [
                    types.TextContent(
                        type="text",
                        text=f"未知工具: {name}",
                    )
                ]
        except Exception as e:
            logger.error(f"工具调用失败: {e}")
            return [
                types.TextContent(
                    type="text", 
                    text=f"工具调用失败: {str(e)}",
                )
            ]

    @app.list_tools()
    async def list_tools() -> list[types.Tool]:
        """返回可用工具列表 - 使用SDK标准接口"""
        logger.info("[SDK] 获取工具列表")
        
        return [
            types.Tool(
                name="get_device_info",
                description="获取设备详细信息，包括状态、型号、系统版本等",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "device_id": {
                            "type": "string",
                            "description": "设备ID或设备名称"
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
            types.Tool(
                name="list_devices",
                description="列出所有可用的测试设备",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "device_type": {
                            "type": "string",
                            "enum": ["android", "ios", "windows", "other", "all"],
                            "description": "过滤设备类型",
                            "default": "all"
                        },
                        "status": {
                            "type": "string",
                            "enum": ["online", "offline", "all"],
                            "description": "过滤设备状态 (online=可用, offline=其他状态)",
                            "default": "all"
                        }
                    }
                }
            ),
            types.Tool(
                name="get_windows_architectures",
                description="获取所有Windows设备的芯片架构列表",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),
            types.Tool(
                name="query_devices_by_architecture",
                description="根据芯片架构查询Windows设备",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "architecture": {
                            "type": "string",
                            "description": "芯片架构，如x64或arm64"
                        }
                    },
                    "required": ["architecture"]
                }
            ),
            types.Tool(
                name="get_device_records",
                description="获取设备借用/归还记录",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "record_type": {
                            "type": "string",
                            "enum": ["all", "借用", "归还"],
                            "description": "记录类型过滤",
                            "default": "all"
                        }
                    }
                }
            ),
            types.Tool(
                name="send_notification_test",
                description="发送测试通知流（演示SDK通知功能）",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "count": {
                            "type": "number",
                            "description": "通知数量",
                            "default": 3
                        },
                        "interval": {
                            "type": "number",
                            "description": "通知间隔（秒）",
                            "default": 1.0
                        },
                        "message": {
                            "type": "string",
                            "description": "通知消息",
                            "default": "设备状态更新"
                        }
                    }
                }
            )
        ]

    @app.list_prompts()
    async def list_prompts() -> list[types.Prompt]:
        """返回可用提示列表 - 使用SDK标准接口"""
        logger.info("[SDK] 获取提示列表")
        
        return [
            types.Prompt(
                name="device_test_plan",
                description="生成设备测试计划模板",
                arguments=[
                    types.PromptArgument(
                        name="device_type",
                        description="设备类型 (android/ios/windows)",
                        required=True
                    ),
                    types.PromptArgument(
                        name="test_scope", 
                        description="测试范围 (功能测试/性能测试/兼容性测试)",
                        required=False
                    )
                ]
            ),
            types.Prompt(
                name="bug_report_template",
                description="生成Bug报告模板",
                arguments=[
                    types.PromptArgument(
                        name="device_id",
                        description="出现问题的设备ID",
                        required=True
                    ),
                    types.PromptArgument(
                        name="severity",
                        description="问题严重程度 (低/中/高/紧急)",
                        required=False
                    )
                ]
            )
        ]

    @app.get_prompt()
    async def get_prompt(name: str, arguments: dict[str, str] | None = None) -> types.GetPromptResult:
        """获取提示内容 - 使用SDK标准接口"""
        args = arguments or {}
        logger.info(f"[SDK] 获取提示: {name}, 参数: {args}")
        
        try:
            if name == "device_test_plan":
                return await _handle_device_test_plan_prompt(args)
            elif name == "bug_report_template":
                return await _handle_bug_report_template_prompt(args)
            else:
                return types.GetPromptResult(
                    description=f"未知提示: {name}",
                    messages=[
                        types.PromptMessage(
                            role="user",
                            content=types.TextContent(
                                type="text",
                                text=f"错误：未找到名为 '{name}' 的提示模板"
                            )
                        )
                    ]
                )
        except Exception as e:
            logger.error(f"提示处理失败: {e}")
            return types.GetPromptResult(
                description="提示处理失败",
                messages=[
                    types.PromptMessage(
                        role="user",
                        content=types.TextContent(
                            type="text",
                            text=f"处理提示时发生错误: {str(e)}"
                        )
                    )
                ]
            )

    # 创建事件存储（支持断点续传）
    event_store = InMemoryEventStore()

    # 创建会话管理器 - 这是关键！使用SDK的StreamableHTTPSessionManager
    session_manager = StreamableHTTPSessionManager(
        app=app,
        event_store=event_store,  # 启用断点续传
        json_response=json_response,
    )

    # ASGI处理器 - 这里才是真正使用SDK处理HTTP请求
    async def handle_streamable_http(scope: Scope, receive: Receive, send: Send) -> None:
        await session_manager.handle_request(scope, receive, send)

    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette) -> AsyncIterator[None]:
        """管理会话管理器生命周期"""
        async with session_manager.run():
            logger.info("SDK StreamableHTTP会话管理器已启动!")
            try:
                yield
            finally:
                logger.info("服务器正在关闭...")

    # 创建ASGI应用 - 使用SDK的传输层
    starlette_app = Starlette(
        debug=True,
        routes=[
            Mount("/mcp", app=handle_streamable_http),  # 这里使用SDK处理
        ],
        lifespan=lifespan,
    )

    # 添加CORS中间件
    starlette_app = CORSMiddleware(
        starlette_app,
        allow_origins=["*"],
        allow_methods=["GET", "POST", "DELETE"],
        expose_headers=["Mcp-Session-Id"],
    )

    logger.info(f"服务器启动在端口 {port}")
    logger.info(f"MCP端点: http://127.0.0.1:{port}/mcp")
    logger.info("使用官方SDK StreamableHTTP传输")

    import uvicorn
    uvicorn.run(starlette_app, host="127.0.0.1", port=port)

    return 0


# 工具实现函数
async def _handle_get_device_info(arguments: dict[str, Any], ctx) -> list[types.ContentBlock]:
    """处理获取设备信息"""
    device_id = arguments.get("device_id")
    device_type = arguments.get("device_type")
    
    if not device_id or not device_type:
        return [types.TextContent(type="text", text="缺少必需参数: device_id 或 device_type")]
    
    # 发送日志通知
    await ctx.session.send_log_message(
        level="info",
        data=f"正在获取设备 {device_id} 的信息...",
        logger="device_manager",
        related_request_id=ctx.request_id,
    )
    
    try:
        # 根据设备类型读取真实设备数据
        devices = []
        if device_type == "android":
            devices = read_android_devices()
        elif device_type == "ios":
            devices = read_ios_devices()
        elif device_type == "windows":
            devices = read_windows_devices()
        else:
            return [types.TextContent(type="text", text=f"不支持的设备类型: {device_type}")]
        
        # 查找指定设备
        device_info = None
        for device in devices:
            # 根据设备名称或序列号匹配
            if (device.get('设备名称') == device_id or 
                device.get('设备序列号') == device_id or
                device_id in str(device.get('设备名称', ''))):
                device_info = device
                break
        
        if not device_info:
            return [types.TextContent(
                type="text", 
                text=f"未找到设备: {device_id} (类型: {device_type})\n可用设备数量: {len(devices)}"
            )]
        
        # 格式化设备信息
        result_text = f"""设备信息获取成功:
设备名称: {device_info.get('设备名称', 'N/A')}
设备类型: {device_type}
设备状态: {device_info.get('设备状态', 'N/A')}
设备OS: {device_info.get('设备OS', 'N/A')}
设备序列号: {device_info.get('设备序列号', 'N/A')}
SKU: {device_info.get('SKU', 'N/A')}
品牌: {device_info.get('品牌', 'N/A')}
借用者: {device_info.get('借用者', '无')}
所属manager: {device_info.get('所属manager', 'N/A')}
资产编号: {device_info.get('资产编号', 'N/A')}
是否盘点: {device_info.get('是否盘点', 'N/A')}
创建日期: {device_info.get('创建日期', 'N/A')}"""

        # 添加Windows特有字段
        if device_type == "windows" and device_info.get('芯片架构'):
            result_text += f"\n芯片架构: {device_info.get('芯片架构', 'N/A')}"
        
        # 添加Android特有字段
        if device_type == "android" and device_info.get('类型'):
            result_text += f"\n类型: {device_info.get('类型', 'N/A')}"
        
        result_text += f"\n\n✨ 此结果来自真实设备数据 (CSV文件)"
        
        logger.info(f"[Real Data] 返回设备信息: {device_info.get('设备名称')}")
        return [types.TextContent(type="text", text=result_text)]
        
    except Exception as e:
        logger.error(f"读取设备信息失败: {e}")
        return [types.TextContent(
            type="text", 
            text=f"读取设备信息失败: {str(e)}\n请检查设备数据文件是否存在"
        )]


async def _handle_list_devices(arguments: dict[str, Any], ctx) -> list[types.ContentBlock]:
    """处理列出设备"""
    device_type = arguments.get("device_type", "all")
    status = arguments.get("status", "all")
    
    # 发送进度通知
    await ctx.session.send_log_message(
        level="info",
        data=f"正在扫描设备 (类型: {device_type}, 状态: {status})...",
        logger="device_scanner",
        related_request_id=ctx.request_id,
    )
    
    try:
        all_devices = []
        
        # 读取各类型设备
        if device_type == "all" or device_type == "android":
            android_devices = read_android_devices()
            for device in android_devices:
                device['device_type'] = 'android'
                all_devices.append(device)
        
        if device_type == "all" or device_type == "ios":
            ios_devices = read_ios_devices()
            for device in ios_devices:
                device['device_type'] = 'ios'
                all_devices.append(device)
        
        if device_type == "all" or device_type == "windows":
            windows_devices = read_windows_devices()
            for device in windows_devices:
                device['device_type'] = 'windows'
                all_devices.append(device)
        
        if device_type == "all" or device_type == "other":
            other_devices = read_other_devices()
            for device in other_devices:
                device['device_type'] = 'other'
                all_devices.append(device)
        
        # 状态过滤
        if status != "all":
            if status == "online":
                # 将"可用"状态映射为"online"
                all_devices = [d for d in all_devices if d.get('设备状态') == '可用']
            elif status == "offline":
                # 将非"可用"状态映射为"offline"
                all_devices = [d for d in all_devices if d.get('设备状态') != '可用']
        
        # 格式化结果
        result_text = f"设备列表 - 类型: {device_type}, 状态: {status}:\n\n"
        
        if not all_devices:
            result_text += "未找到符合条件的设备。\n"
        else:
            # 按设备类型分组显示
            device_groups = {}
            for device in all_devices:
                dtype = device.get('device_type', 'unknown')
                if dtype not in device_groups:
                    device_groups[dtype] = []
                device_groups[dtype].append(device)
            
            for dtype, devices in device_groups.items():
                result_text += f"📱 {dtype.upper()} 设备 ({len(devices)}台):\n"
                for device in devices:
                    device_name = device.get('设备名称', 'N/A')
                    device_status = device.get('设备状态', 'N/A')
                    device_os = device.get('设备OS', 'N/A')
                    borrower = device.get('借用者', '无')
                    
                    result_text += f"  • {device_name}\n"
                    result_text += f"    状态: {device_status} | 系统: {device_os}\n"
                    result_text += f"    借用者: {borrower}\n"
                    
                    # 添加特殊字段
                    if dtype == "windows" and device.get('芯片架构'):
                        result_text += f"    架构: {device.get('芯片架构')}\n"
                    elif dtype == "android" and device.get('类型'):
                        result_text += f"    类型: {device.get('类型')}\n"
                    
                    result_text += "\n"
                result_text += "\n"
        
        # 统计信息
        total_count = len(all_devices)
        available_count = sum(1 for d in all_devices if d.get('设备状态') == '可用')
        in_use_count = sum(1 for d in all_devices if d.get('设备状态') == '正在使用')
        
        result_text += f"📊 统计信息:\n"
        result_text += f"总设备数: {total_count}\n"
        result_text += f"可用设备: {available_count}\n"
        result_text += f"使用中设备: {in_use_count}\n"
        result_text += f"其他状态: {total_count - available_count - in_use_count}\n"
        result_text += f"\n✨ 此结果来自真实设备数据 (CSV文件)"
        
        logger.info(f"[Real Data] 返回设备列表: {total_count}个设备")
        return [types.TextContent(type="text", text=result_text)]
        
    except Exception as e:
        logger.error(f"读取设备列表失败: {e}")
        return [types.TextContent(
            type="text", 
            text=f"读取设备列表失败: {str(e)}\n请检查设备数据文件是否存在"
        )]


async def _handle_notification_test(arguments: dict[str, Any], ctx) -> list[types.ContentBlock]:
    """处理通知测试 - 演示SDK的通知功能"""
    count = arguments.get("count", 3)
    interval = arguments.get("interval", 1.0)
    message = arguments.get("message", "设备状态更新")
    
    # 发送多个通知（演示StreamableHTTP的实时通知功能）
    for i in range(count):
        notification_msg = f"[{i + 1}/{count}] {message} - SDK实时通知测试"
        await ctx.session.send_log_message(
            level="info",
            data=notification_msg,
            logger="notification_test",
            related_request_id=ctx.request_id,
        )
        logger.info(f"[SDK] 发送通知 {i + 1}/{count}")
        
        if i < count - 1:  # 最后一个通知后不等待
            await anyio.sleep(interval)
    
    return [
        types.TextContent(
            type="text",
            text=f"✅ SDK通知测试完成: 发送了 {count} 个通知，间隔 {interval}秒\n\n通知内容: {message}\n\n✨ 使用官方MCP SDK StreamableHTTP实时通知功能",
        )
    ]


async def _handle_get_windows_architectures(arguments: dict[str, Any], ctx) -> list[types.ContentBlock]:
    """处理获取Windows架构列表"""
    await ctx.session.send_log_message(
        level="info",
        data="正在获取Windows设备架构列表...",
        logger="windows_architecture",
        related_request_id=ctx.request_id,
    )
    
    try:
        architectures = get_all_architectures()
        
        result_text = f"Windows设备芯片架构列表:\n\n"
        for i, arch in enumerate(architectures, 1):
            result_text += f"{i}. {arch}\n"
        
        result_text += f"\n共找到 {len(architectures)} 种架构"
        result_text += f"\n\n✨ 此结果来自真实Windows设备数据 (CSV文件)"
        
        logger.info(f"[Real Data] 返回Windows架构: {len(architectures)}种")
        return [types.TextContent(type="text", text=result_text)]
        
    except Exception as e:
        logger.error(f"获取Windows架构失败: {e}")
        return [types.TextContent(
            type="text", 
            text=f"获取Windows架构失败: {str(e)}\n请检查Windows设备数据文件是否存在"
        )]


async def _handle_query_devices_by_architecture(arguments: dict[str, Any], ctx) -> list[types.ContentBlock]:
    """处理按架构查询Windows设备"""
    architecture = arguments.get("architecture")
    
    if not architecture:
        return [types.TextContent(type="text", text="缺少必需参数: architecture")]
    
    await ctx.session.send_log_message(
        level="info",
        data=f"正在查询架构为 {architecture} 的Windows设备...",
        logger="architecture_query",
        related_request_id=ctx.request_id,
    )
    
    try:
        devices = query_devices_by_architecture(architecture)
        
        result_text = f"架构 '{architecture}' 的Windows设备:\n\n"
        
        if not devices:
            result_text += f"未找到架构为 '{architecture}' 的设备。\n"
            # 显示可用架构
            all_archs = get_all_architectures()
            result_text += f"\n可用架构: {', '.join(all_archs)}"
        else:
            for i, device in enumerate(devices, 1):
                device_name = device.get('设备名称', 'N/A')
                device_status = device.get('设备状态', 'N/A')
                device_os = device.get('设备OS', 'N/A')
                borrower = device.get('借用者', '无')
                sku = device.get('SKU', 'N/A')
                
                result_text += f"{i}. {device_name}\n"
                result_text += f"   状态: {device_status}\n"
                result_text += f"   系统: {device_os}\n"
                result_text += f"   SKU: {sku}\n"
                result_text += f"   借用者: {borrower}\n"
                result_text += f"   架构: {device.get('芯片架构', 'N/A')}\n\n"
            
            # 统计信息
            available_count = sum(1 for d in devices if d.get('设备状态') == '可用')
            in_use_count = sum(1 for d in devices if d.get('设备状态') == '正在使用')
            
            result_text += f"📊 {architecture} 架构统计:\n"
            result_text += f"总设备数: {len(devices)}\n"
            result_text += f"可用设备: {available_count}\n"
            result_text += f"使用中设备: {in_use_count}\n"
        
        result_text += f"\n✨ 此结果来自真实Windows设备数据 (CSV文件)"
        
        logger.info(f"[Real Data] 返回架构'{architecture}'设备: {len(devices)}台")
        return [types.TextContent(type="text", text=result_text)]
        
    except Exception as e:
        logger.error(f"按架构查询设备失败: {e}")
        return [types.TextContent(
            type="text", 
            text=f"按架构查询设备失败: {str(e)}\n请检查Windows设备数据文件是否存在"
        )]


async def _handle_get_device_records(arguments: dict[str, Any], ctx) -> list[types.ContentBlock]:
    """处理获取设备记录"""
    record_type = arguments.get("record_type", "all")
    
    await ctx.session.send_log_message(
        level="info",
        data=f"正在获取设备记录 (类型: {record_type})...",
        logger="device_records",
        related_request_id=ctx.request_id,
    )
    
    try:
        records = read_records()
        
        # 过滤记录类型
        if record_type != "all":
            records = [r for r in records if r.get('状态') == record_type]
        
        result_text = f"设备借用/归还记录 (类型: {record_type}):\n\n"
        
        if not records:
            result_text += "未找到符合条件的记录。\n"
        else:
            # 按状态分组
            borrow_records = [r for r in records if r.get('状态') == '借用']
            return_records = [r for r in records if r.get('状态') == '归还']
            
            if record_type == "all" or record_type == "借用":
                result_text += f"📝 借用记录 ({len(borrow_records)}条):\n"
                for i, record in enumerate(borrow_records, 1):
                    result_text += f"{i}. 借用者: {record.get('借用者', 'N/A')}\n"
                    result_text += f"   设备: {record.get('设备', 'N/A')}\n"
                    result_text += f"   资产编号: {record.get('资产编号', 'N/A')}\n"
                    result_text += f"   创建日期: {record.get('创建日期', 'N/A')}\n"
                    result_text += f"   原因: {record.get('原因', 'N/A')}\n\n"
                result_text += "\n"
            
            if record_type == "all" or record_type == "归还":
                result_text += f"📤 归还记录 ({len(return_records)}条):\n"
                for i, record in enumerate(return_records, 1):
                    result_text += f"{i}. 归还者: {record.get('借用者', 'N/A')}\n"
                    result_text += f"   设备: {record.get('设备', 'N/A')}\n"
                    result_text += f"   资产编号: {record.get('资产编号', 'N/A')}\n"
                    result_text += f"   创建日期: {record.get('创建日期', 'N/A')}\n"
                    result_text += f"   原因: {record.get('原因', 'N/A')}\n\n"
            
            # 统计信息
            result_text += f"📊 记录统计:\n"
            result_text += f"总记录数: {len(records)}\n"
            result_text += f"借用记录: {len(borrow_records)}\n"
            result_text += f"归还记录: {len(return_records)}\n"
        
        result_text += f"\n✨ 此结果来自真实设备记录数据 (CSV文件)"
        
        logger.info(f"[Real Data] 返回设备记录: {len(records)}条")
        return [types.TextContent(type="text", text=result_text)]
        
    except Exception as e:
        logger.error(f"获取设备记录失败: {e}")
        return [types.TextContent(
            type="text", 
            text=f"获取设备记录失败: {str(e)}\n请检查设备记录文件是否存在"
        )]


# 提示实现函数
async def _handle_device_test_plan_prompt(arguments: dict[str, str]) -> types.GetPromptResult:
    """处理设备测试计划提示"""
    device_type = arguments.get("device_type", "通用")
    test_scope = arguments.get("test_scope", "功能测试")
    
    prompt_content = f"""
# {device_type.upper()} 设备测试计划 (SDK版本)

## 测试范围: {test_scope}

## 测试环境
- 设备类型: {device_type}
- 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- 生成方式: 官方MCP SDK StreamableHTTP

## 测试用例

### 1. 基础功能测试 (SDK增强)
- [ ] 设备连接测试
- [ ] 设备信息获取
- [ ] 屏幕截图功能
- [ ] 应用安装/卸载
- [ ] 实时通知测试 ✨

### 2. 性能测试 (SDK监控)
- [ ] CPU使用率监控
- [ ] 内存使用率监控
- [ ] 网络连接测试
- [ ] 电池消耗测试
- [ ] 实时性能数据流 ✨

### 3. 兼容性测试
- [ ] 不同版本系统测试
- [ ] 不同分辨率适配
- [ ] 多设备并发测试
- [ ] 断点续传功能测试 ✨

## 预期结果
所有测试用例都应该通过，设备应该保持稳定运行状态。

## 注意事项
- 测试前确保设备已正确连接
- 记录所有异常情况和错误日志
- 测试完成后生成详细报告
- 使用SDK的实时通知功能监控测试进度 ✨

## SDK特性
- ✅ 实时通知和进度报告
- ✅ 断点续传支持
- ✅ 结构化错误处理
- ✅ 会话管理
"""
    
    return types.GetPromptResult(
        description="设备测试计划 (SDK版本)",
        messages=[
            types.PromptMessage(
                role="user",
                content=types.TextContent(type="text", text=prompt_content)
            )
        ]
    )


async def _handle_bug_report_template_prompt(arguments: dict[str, str]) -> types.GetPromptResult:
    """处理Bug报告模板提示"""
    device_id = arguments.get("device_id", "未指定")
    severity = arguments.get("severity", "中")
    
    prompt_content = f"""
# Bug报告 (SDK版本)

## 基本信息
- 报告时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- 设备ID: {device_id}
- 严重程度: {severity}
- 报告人: [请填写]
- 生成方式: 官方MCP SDK StreamableHTTP ✨

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
- MCP传输: StreamableHTTP ✨

## 附加信息
- 错误日志: [如有请附上]
- 截图/视频: [如有请附上]
- 实时通知日志: [SDK自动记录] ✨
- 其他相关信息: [请补充]

## 影响范围
[描述此问题可能影响的功能或用户]

## SDK诊断信息 ✨
- 会话ID: [自动记录]
- 请求ID: [自动记录]  
- 事件流状态: [自动记录]
- 断点续传支持: 已启用

## 解决方案建议
[如有解决方案建议请填写]
"""
    
    return types.GetPromptResult(
        description="Bug报告模板 (SDK版本)",
        messages=[
            types.PromptMessage(
                role="user",
                content=types.TextContent(type="text", text=prompt_content)
            )
        ]
    )


if __name__ == "__main__":
    main()
