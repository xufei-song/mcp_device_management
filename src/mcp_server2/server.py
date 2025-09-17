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
from src.device.records_reader import (
    read_records, 
    find_device_by_asset_number,
    borrow_device,
    return_device,
    add_borrow_record,
    add_return_record
)

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
            elif name == "find_device_by_asset":
                return await _handle_find_device_by_asset(arguments, ctx)
            elif name == "borrow_device":
                return await _handle_borrow_device(arguments, ctx)
            elif name == "return_device":
                return await _handle_return_device(arguments, ctx)
            elif name == "add_borrow_record":
                return await _handle_add_borrow_record(arguments, ctx)
            elif name == "add_return_record":
                return await _handle_add_return_record(arguments, ctx)
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
            ),
            types.Tool(
                name="find_device_by_asset",
                description="根据资产编号查找设备信息",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "asset_number": {
                            "type": "string",
                            "description": "设备资产编号"
                        }
                    },
                    "required": ["asset_number"]
                }
            ),
            types.Tool(
                name="borrow_device",
                description="借用设备（完整流程：添加借用记录+更新设备状态）",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "asset_number": {
                            "type": "string",
                            "description": "设备资产编号"
                        },
                        "borrower": {
                            "type": "string",
                            "description": "借用者姓名"
                        },
                        "reason": {
                            "type": "string",
                            "description": "借用原因（可选）",
                            "default": ""
                        }
                    },
                    "required": ["asset_number", "borrower"]
                }
            ),
            types.Tool(
                name="return_device",
                description="归还设备（完整流程：添加归还记录+更新设备状态）",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "asset_number": {
                            "type": "string",
                            "description": "设备资产编号"
                        },
                        "borrower": {
                            "type": "string",
                            "description": "归还者姓名"
                        },
                        "reason": {
                            "type": "string",
                            "description": "归还原因（可选）",
                            "default": ""
                        }
                    },
                    "required": ["asset_number", "borrower"]
                }
            ),
            types.Tool(
                name="add_borrow_record",
                description="仅添加借用记录（不更新设备状态）",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "asset_number": {
                            "type": "string",
                            "description": "设备资产编号"
                        },
                        "borrower": {
                            "type": "string",
                            "description": "借用者姓名"
                        },
                        "reason": {
                            "type": "string",
                            "description": "借用原因（可选）",
                            "default": ""
                        }
                    },
                    "required": ["asset_number", "borrower"]
                }
            ),
            types.Tool(
                name="add_return_record",
                description="仅添加归还记录（不更新设备状态）",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "asset_number": {
                            "type": "string",
                            "description": "设备资产编号"
                        },
                        "borrower": {
                            "type": "string",
                            "description": "归还者姓名"
                        },
                        "reason": {
                            "type": "string",
                            "description": "归还原因（可选）",
                            "default": ""
                        }
                    },
                    "required": ["asset_number", "borrower"]
                }
            )
        ]

    @app.list_prompts()
    async def list_prompts() -> list[types.Prompt]:
        """返回可用提示列表 - 使用SDK标准接口"""
        logger.info("[SDK] 获取提示列表")
        
        return [
            types.Prompt(
                name="device_info_query",
                description="生成设备信息查询指导",
                arguments=[
                    types.PromptArgument(
                        name="device_type",
                        description="要查询的设备类型 (android/ios/windows)",
                        required=False
                    )
                ]
            ),
            types.Prompt(
                name="device_list_guide",
                description="生成设备列表查询和筛选指导",
                arguments=[
                    types.PromptArgument(
                        name="filter_type",
                        description="筛选类型 (all/available/in_use)",
                        required=False
                    )
                ]
            ),
            types.Prompt(
                name="asset_lookup_guide",
                description="生成资产编号查询指导",
                arguments=[
                    types.PromptArgument(
                        name="asset_pattern",
                        description="资产编号模式示例",
                        required=False
                    )
                ]
            ),
            types.Prompt(
                name="device_borrow_workflow",
                description="生成设备借用流程指导",
                arguments=[
                    types.PromptArgument(
                        name="borrower_type",
                        description="借用者类型 (developer/tester/manager)",
                        required=False
                    )
                ]
            ),
            types.Prompt(
                name="device_return_workflow",
                description="生成设备归还流程指导",
                arguments=[
                    types.PromptArgument(
                        name="return_condition",
                        description="归还条件 (normal/damaged/lost)",
                        required=False
                    )
                ]
            ),
            types.Prompt(
                name="windows_architecture_guide",
                description="生成Windows设备架构查询指导",
                arguments=[
                    types.PromptArgument(
                        name="target_arch",
                        description="目标架构 (x64/arm64)",
                        required=False
                    )
                ]
            ),
            types.Prompt(
                name="device_records_analysis",
                description="生成设备记录分析模板",
                arguments=[
                    types.PromptArgument(
                        name="analysis_type",
                        description="分析类型 (usage/trends/issues)",
                        required=False
                    ),
                    types.PromptArgument(
                        name="time_period",
                        description="时间范围 (daily/weekly/monthly)",
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
            if name == "device_info_query":
                return await _handle_device_info_query_prompt(args)
            elif name == "device_list_guide":
                return await _handle_device_list_guide_prompt(args)
            elif name == "asset_lookup_guide":
                return await _handle_asset_lookup_guide_prompt(args)
            elif name == "device_borrow_workflow":
                return await _handle_device_borrow_workflow_prompt(args)
            elif name == "device_return_workflow":
                return await _handle_device_return_workflow_prompt(args)
            elif name == "windows_architecture_guide":
                return await _handle_windows_architecture_guide_prompt(args)
            elif name == "device_records_analysis":
                return await _handle_device_records_analysis_prompt(args)
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
async def _handle_find_device_by_asset(arguments: dict[str, Any], ctx) -> list[types.ContentBlock]:
    """处理根据资产编号查找设备"""
    asset_number = arguments.get("asset_number")
    
    if not asset_number:
        return [types.TextContent(type="text", text="缺少必需参数: asset_number")]
    
    await ctx.session.send_log_message(
        level="info",
        data=f"正在查找资产编号 {asset_number} 的设备...",
        logger="asset_finder",
        related_request_id=ctx.request_id,
    )
    
    try:
        device_info, device_type = find_device_by_asset_number(asset_number)
        
        if not device_info:
            result_text = f"❌ 未找到资产编号为 '{asset_number}' 的设备\n\n"
            result_text += "请检查资产编号是否正确，或使用 list_devices 工具查看所有可用设备。"
        else:
            result_text = f"✅ 找到设备信息:\n\n"
            result_text += f"🏷️ 资产编号: {asset_number}\n"
            result_text += f"📱 设备名称: {device_info.get('设备名称', 'N/A')}\n"
            result_text += f"🔧 设备类型: {device_type}\n"
            result_text += f"📋 设备状态: {device_info.get('设备状态', 'N/A')}\n"
            result_text += f"🖥️ 设备OS: {device_info.get('设备OS', 'N/A')}\n"
            result_text += f"🏭 品牌: {device_info.get('品牌', 'N/A')}\n"
            result_text += f"👤 当前借用者: {device_info.get('借用者', '无')}\n"
            result_text += f"👨‍💼 所属manager: {device_info.get('所属manager', 'N/A')}\n"
            result_text += f"🔢 设备序列号: {device_info.get('设备序列号', 'N/A')}\n"
            result_text += f"📅 创建日期: {device_info.get('创建日期', 'N/A')}\n"
            
            # 添加特殊字段
            if device_type == "windows" and device_info.get('芯片架构'):
                result_text += f"💻 芯片架构: {device_info.get('芯片架构', 'N/A')}\n"
            
            if device_type == "android" and device_info.get('类型'):
                result_text += f"📱 类型: {device_info.get('类型', 'N/A')}\n"
            
            result_text += f"\n✨ 此结果来自真实设备数据 (CSV文件)"
        
        logger.info(f"[Asset Search] 查找资产编号 {asset_number}: {'找到' if device_info else '未找到'}")
        return [types.TextContent(type="text", text=result_text)]
        
    except Exception as e:
        logger.error(f"查找设备失败: {e}")
        return [types.TextContent(
            type="text", 
            text=f"查找设备失败: {str(e)}\n请检查资产编号格式或联系管理员"
        )]


async def _handle_borrow_device(arguments: dict[str, Any], ctx) -> list[types.ContentBlock]:
    """处理设备借用（完整流程）"""
    asset_number = arguments.get("asset_number")
    borrower = arguments.get("borrower")
    reason = arguments.get("reason", "")
    
    if not asset_number or not borrower:
        return [types.TextContent(type="text", text="缺少必需参数: asset_number 或 borrower")]
    
    await ctx.session.send_log_message(
        level="info",
        data=f"正在执行设备借用操作: 资产编号 {asset_number}, 借用者 {borrower}...",
        logger="device_borrow",
        related_request_id=ctx.request_id,
    )
    
    try:
        # 执行借用操作
        success = borrow_device(asset_number, borrower, reason)
        
        if success:
            result_text = f"🎉 设备借用成功！\n\n"
            result_text += f"🏷️ 资产编号: {asset_number}\n"
            result_text += f"👤 借用者: {borrower}\n"
            if reason:
                result_text += f"💬 借用原因: {reason}\n"
            result_text += f"📅 借用时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            result_text += f"📋 设备状态: 已更新为'正在使用'\n"
            result_text += f"📝 记录状态: 已添加到借用记录\n"
            result_text += f"\n✨ 完整借用流程已完成 (记录+状态更新)"
            
            # 发送成功通知
            await ctx.session.send_log_message(
                level="info",
                data=f"✅ 设备借用成功: {asset_number} -> {borrower}",
                logger="device_borrow",
                related_request_id=ctx.request_id,
            )
        else:
            result_text = f"❌ 设备借用失败\n\n"
            result_text += f"🏷️ 资产编号: {asset_number}\n"
            result_text += f"👤 借用者: {borrower}\n"
            result_text += f"❗ 可能原因:\n"
            result_text += f"  • 资产编号不存在\n"
            result_text += f"  • 设备已被借用\n"
            result_text += f"  • 设备状态异常\n"
            result_text += f"  • 系统内部错误\n"
            result_text += f"\n💡 建议使用 find_device_by_asset 工具检查设备状态"
        
        logger.info(f"[Device Borrow] 资产编号 {asset_number}: {'成功' if success else '失败'}")
        return [types.TextContent(type="text", text=result_text)]
        
    except Exception as e:
        logger.error(f"设备借用失败: {e}")
        return [types.TextContent(
            type="text", 
            text=f"设备借用操作失败: {str(e)}\n请检查参数或联系管理员"
        )]


async def _handle_return_device(arguments: dict[str, Any], ctx) -> list[types.ContentBlock]:
    """处理设备归还（完整流程）"""
    asset_number = arguments.get("asset_number")
    borrower = arguments.get("borrower")
    reason = arguments.get("reason", "")
    
    if not asset_number or not borrower:
        return [types.TextContent(type="text", text="缺少必需参数: asset_number 或 borrower")]
    
    await ctx.session.send_log_message(
        level="info",
        data=f"正在执行设备归还操作: 资产编号 {asset_number}, 归还者 {borrower}...",
        logger="device_return",
        related_request_id=ctx.request_id,
    )
    
    try:
        # 执行归还操作
        success = return_device(asset_number, borrower, reason)
        
        if success:
            result_text = f"🎉 设备归还成功！\n\n"
            result_text += f"🏷️ 资产编号: {asset_number}\n"
            result_text += f"👤 归还者: {borrower}\n"
            if reason:
                result_text += f"💬 归还原因: {reason}\n"
            result_text += f"📅 归还时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            result_text += f"📋 设备状态: 已更新为'可用'\n"
            result_text += f"👤 借用者信息: 已清空\n"
            result_text += f"📝 记录状态: 已添加到归还记录\n"
            result_text += f"\n✨ 完整归还流程已完成 (记录+状态更新)"
            
            # 发送成功通知
            await ctx.session.send_log_message(
                level="info",
                data=f"✅ 设备归还成功: {asset_number} <- {borrower}",
                logger="device_return",
                related_request_id=ctx.request_id,
            )
        else:
            result_text = f"❌ 设备归还失败\n\n"
            result_text += f"🏷️ 资产编号: {asset_number}\n"
            result_text += f"👤 归还者: {borrower}\n"
            result_text += f"❗ 可能原因:\n"
            result_text += f"  • 资产编号不存在\n"
            result_text += f"  • 设备未被借用\n"
            result_text += f"  • 归还者与借用者不匹配\n"
            result_text += f"  • 系统内部错误\n"
            result_text += f"\n💡 建议使用 find_device_by_asset 工具检查设备状态"
        
        logger.info(f"[Device Return] 资产编号 {asset_number}: {'成功' if success else '失败'}")
        return [types.TextContent(type="text", text=result_text)]
        
    except Exception as e:
        logger.error(f"设备归还失败: {e}")
        return [types.TextContent(
            type="text", 
            text=f"设备归还操作失败: {str(e)}\n请检查参数或联系管理员"
        )]


async def _handle_add_borrow_record(arguments: dict[str, Any], ctx) -> list[types.ContentBlock]:
    """处理添加借用记录（仅记录）"""
    asset_number = arguments.get("asset_number")
    borrower = arguments.get("borrower")
    reason = arguments.get("reason", "")
    
    if not asset_number or not borrower:
        return [types.TextContent(type="text", text="缺少必需参数: asset_number 或 borrower")]
    
    await ctx.session.send_log_message(
        level="info",
        data=f"正在添加借用记录: 资产编号 {asset_number}, 借用者 {borrower}...",
        logger="borrow_record",
        related_request_id=ctx.request_id,
    )
    
    try:
        # 添加借用记录
        success = add_borrow_record(asset_number, borrower, reason)
        
        if success:
            result_text = f"✅ 借用记录添加成功！\n\n"
            result_text += f"🏷️ 资产编号: {asset_number}\n"
            result_text += f"👤 借用者: {borrower}\n"
            if reason:
                result_text += f"💬 借用原因: {reason}\n"
            result_text += f"📅 记录时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            result_text += f"📝 记录状态: 已添加到records.csv\n"
            result_text += f"⚠️ 注意: 此操作仅添加记录，不会更新设备状态\n"
            result_text += f"\n💡 如需完整借用流程，请使用 borrow_device 工具"
        else:
            result_text = f"❌ 借用记录添加失败\n\n"
            result_text += f"🏷️ 资产编号: {asset_number}\n"
            result_text += f"👤 借用者: {borrower}\n"
            result_text += f"❗ 可能原因:\n"
            result_text += f"  • 资产编号不存在\n"
            result_text += f"  • 参数格式错误\n"
            result_text += f"  • 文件写入权限问题\n"
            result_text += f"\n💡 建议使用 find_device_by_asset 工具检查资产编号"
        
        logger.info(f"[Borrow Record] 资产编号 {asset_number}: {'成功' if success else '失败'}")
        return [types.TextContent(type="text", text=result_text)]
        
    except Exception as e:
        logger.error(f"添加借用记录失败: {e}")
        return [types.TextContent(
            type="text", 
            text=f"添加借用记录失败: {str(e)}\n请检查参数或联系管理员"
        )]


async def _handle_add_return_record(arguments: dict[str, Any], ctx) -> list[types.ContentBlock]:
    """处理添加归还记录（仅记录）"""
    asset_number = arguments.get("asset_number")
    borrower = arguments.get("borrower")
    reason = arguments.get("reason", "")
    
    if not asset_number or not borrower:
        return [types.TextContent(type="text", text="缺少必需参数: asset_number 或 borrower")]
    
    await ctx.session.send_log_message(
        level="info",
        data=f"正在添加归还记录: 资产编号 {asset_number}, 归还者 {borrower}...",
        logger="return_record",
        related_request_id=ctx.request_id,
    )
    
    try:
        # 添加归还记录
        success = add_return_record(asset_number, borrower, reason)
        
        if success:
            result_text = f"✅ 归还记录添加成功！\n\n"
            result_text += f"🏷️ 资产编号: {asset_number}\n"
            result_text += f"👤 归还者: {borrower}\n"
            if reason:
                result_text += f"💬 归还原因: {reason}\n"
            result_text += f"📅 记录时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            result_text += f"📝 记录状态: 已添加到records.csv\n"
            result_text += f"⚠️ 注意: 此操作仅添加记录，不会更新设备状态\n"
            result_text += f"\n💡 如需完整归还流程，请使用 return_device 工具"
        else:
            result_text = f"❌ 归还记录添加失败\n\n"
            result_text += f"🏷️ 资产编号: {asset_number}\n"
            result_text += f"👤 归还者: {borrower}\n"
            result_text += f"❗ 可能原因:\n"
            result_text += f"  • 资产编号不存在\n"
            result_text += f"  • 参数格式错误\n"
            result_text += f"  • 文件写入权限问题\n"
            result_text += f"\n💡 建议使用 find_device_by_asset 工具检查资产编号"
        
        logger.info(f"[Return Record] 资产编号 {asset_number}: {'成功' if success else '失败'}")
        return [types.TextContent(type="text", text=result_text)]
        
    except Exception as e:
        logger.error(f"添加归还记录失败: {e}")
        return [types.TextContent(
            type="text", 
            text=f"添加归还记录失败: {str(e)}\n请检查参数或联系管理员"
        )]


async def _handle_device_info_query_prompt(arguments: dict[str, str]) -> types.GetPromptResult:
    """处理设备信息查询指导提示"""
    device_type = arguments.get("device_type", "通用")
    
    prompt_content = f"""
# 设备信息查询指导

## 查询设备类型: {device_type}

## 查询步骤

### 1. 基础查询
使用 `get_device_info` 工具查询设备详细信息：
- **设备ID**: 设备名称或序列号
- **设备类型**: android, ios, windows

### 2. 设备类型特点

#### Android设备查询
- 支持设备名称查询（如：Pixel 6）
- 支持序列号查询
- 包含设备类型信息（手机/平板）

#### iOS设备查询  
- 支持设备名称查询（如：iPhone 14）
- 支持序列号查询
- 系统版本信息详细

#### Windows设备查询
- 支持设备名称查询（如：Surface Pro）
- 支持序列号查询
- 包含芯片架构信息（x64/arm64）

### 3. 查询示例

```
工具调用示例:
get_device_info(device_id="设备名称或序列号", device_type="android")
```

### 4. 可查询信息
- 设备名称和序列号
- 设备状态（可用/正在使用/设备异常）
- 当前借用者信息
- 所属manager
- 资产编号
- SKU和品牌信息
- 创建日期

### 5. 故障排除
- 确保设备ID正确
- 检查设备类型匹配
- 使用 list_devices 查看所有可用设备

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    return types.GetPromptResult(
        description="设备信息查询指导",
        messages=[
            types.PromptMessage(
                role="user",
                content=types.TextContent(type="text", text=prompt_content)
            )
        ]
    )


async def _handle_device_list_guide_prompt(arguments: dict[str, str]) -> types.GetPromptResult:
    """处理设备列表查询指导提示"""
    filter_type = arguments.get("filter_type", "all")
    
    prompt_content = f"""
# 设备列表查询和筛选指导

## 当前筛选类型: {filter_type}

## 查询方式

### 1. 基础列表查询
使用 `list_devices` 工具获取设备列表：

```
list_devices(device_type="all", status="all")
```

### 2. 设备类型筛选

#### 支持的设备类型
- **android**: Android手机和平板
- **ios**: iPhone和iPad设备  
- **windows**: Windows PC和Surface
- **other**: 其他类型设备
- **all**: 所有设备类型

### 3. 状态筛选

#### 设备状态类型
- **online**: 可用设备（设备状态="可用"）
- **offline**: 其他状态设备（正在使用/设备异常等）
- **all**: 所有状态设备

### 4. 常用查询场景

#### 查找可用设备
```
list_devices(device_type="android", status="online")
```

#### 查看使用中设备
```
list_devices(device_type="all", status="offline")
```

#### 特定平台设备
```
list_devices(device_type="ios", status="all")
```

### 5. 结果信息
每个设备显示：
- 设备名称和序列号
- 当前状态
- 借用者信息
- 资产编号
- 设备规格信息

### 6. 统计信息
查询结果包含：
- 总设备数量
- 可用设备数量
- 使用中设备数量
- 按类型分组统计

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    return types.GetPromptResult(
        description="设备列表查询指导",
        messages=[
            types.PromptMessage(
                role="user",
                content=types.TextContent(type="text", text=prompt_content)
            )
        ]
    )


async def _handle_asset_lookup_guide_prompt(arguments: dict[str, str]) -> types.GetPromptResult:
    """处理资产编号查询指导提示"""
    asset_pattern = arguments.get("asset_pattern", "18294886")
    
    prompt_content = f"""
# 资产编号查询指导

## 示例资产编号: {asset_pattern}

## 查询方式

### 1. 精确查询
使用 `find_device_by_asset` 工具通过资产编号查找设备：

```
find_device_by_asset(asset_number="{asset_pattern}")
```

### 2. 资产编号特点

#### 编号格式
- 通常为8位数字（如：18294886）
- 每台设备都有唯一的资产编号
- 在设备标签上标识

#### 查询范围
- 自动搜索所有设备类型
- Android设备表
- iOS设备表  
- Windows设备表
- 其他设备表

### 3. 查询结果

#### 成功查询显示
- 🏷️ 资产编号
- 📱 设备名称
- 🔧 设备类型
- 📋 设备状态
- 👤 当前借用者
- 🖥️ 系统信息
- 🏭 品牌信息

#### 查询失败处理
- 检查资产编号是否正确
- 确认设备是否已录入系统
- 使用 list_devices 查看所有设备

### 4. 资产编号作用

#### 设备管理
- 唯一标识设备
- 借用和归还记录
- 设备状态追踪
- 库存管理

#### 相关操作
- 设备借用：borrow_device
- 设备归还：return_device
- 状态查询：get_device_info

### 5. 常见问题

#### 找不到设备
- 确认资产编号无误
- 检查是否为8位数字
- 联系设备管理员确认

#### 多个结果
- 系统确保唯一性
- 每个资产编号对应一台设备

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    return types.GetPromptResult(
        description="资产编号查询指导",
        messages=[
            types.PromptMessage(
                role="user",
                content=types.TextContent(type="text", text=prompt_content)
            )
        ]
    )


async def _handle_device_borrow_workflow_prompt(arguments: dict[str, str]) -> types.GetPromptResult:
    """处理设备借用流程指导提示"""
    borrower_type = arguments.get("borrower_type", "developer")
    
    prompt_content = f"""
# 设备借用流程指导

## 借用者类型: {borrower_type}

## 完整借用流程

### 1. 准备工作

#### 确认设备信息
- 使用 `find_device_by_asset` 查找目标设备
- 确认设备状态为"可用"
- 记录资产编号

#### 借用者信息
- 确认借用者姓名
- 准备借用原因说明

### 2. 执行借用

#### 使用 borrow_device 工具
```
borrow_device(
    asset_number="资产编号",
    borrower="借用者姓名", 
    reason="借用原因"
)
```

#### 流程说明
此工具执行完整借用流程：
1. ✅ 添加借用记录到records.csv
2. ✅ 更新设备状态为"正在使用"
3. ✅ 设置设备借用者信息

### 3. 借用场景

#### 开发人员借用
- 用途：应用开发测试
- 建议时长：1-2周
- 常见设备：Android/iOS测试机

#### 测试人员借用  
- 用途：功能验证测试
- 建议时长：3-5天
- 常见设备：各型号真机

#### 管理人员借用
- 用途：演示或临时使用
- 建议时长：1-3天
- 常见设备：高端设备

### 4. 注意事项

#### 借用前检查
- 设备是否可用
- 设备是否有已知问题
- 预计使用时长

#### 借用期间
- 妥善保管设备
- 及时报告设备问题
- 按时归还设备

#### 借用记录
- 系统自动记录借用时间
- 记录借用原因
- 更新设备状态

### 5. 相关工具

#### 仅记录操作
如果只需要添加借用记录而不更新设备状态：
```
add_borrow_record(asset_number, borrower, reason)
```

#### 查询借用记录
```
get_device_records(record_type="借用")
```

### 6. 故障排除

#### 借用失败原因
- 资产编号不存在
- 设备已被借用
- 设备状态异常
- 参数格式错误

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    return types.GetPromptResult(
        description="设备借用流程指导",
        messages=[
            types.PromptMessage(
                role="user",
                content=types.TextContent(type="text", text=prompt_content)
            )
        ]
    )


async def _handle_device_return_workflow_prompt(arguments: dict[str, str]) -> types.GetPromptResult:
    """处理设备归还流程指导提示"""
    return_condition = arguments.get("return_condition", "normal")
    
    prompt_content = f"""
# 设备归还流程指导

## 归还条件: {return_condition}

## 完整归还流程

### 1. 归还准备

#### 检查设备状态
- 确认设备功能正常
- 清理个人数据和应用
- 恢复设备初始设置

#### 归还信息准备
- 确认资产编号
- 准备归还原因说明
- 确认归还者身份

### 2. 执行归还

#### 使用 return_device 工具
```
return_device(
    asset_number="资产编号",
    borrower="归还者姓名",
    reason="归还原因"
)
```

#### 流程说明
此工具执行完整归还流程：
1. ✅ 添加归还记录到records.csv
2. ✅ 更新设备状态为"可用"
3. ✅ 清空设备借用者信息

### 3. 归还场景

#### 正常归还 (normal)
- 设备功能完好
- 使用完毕主动归还
- 按计划时间归还

#### 损坏归还 (damaged)
- 设备有功能问题
- 需要维修处理
- 详细说明损坏情况

#### 丢失处理 (lost)
- 设备遗失情况
- 需要特殊处理流程
- 联系设备管理员

### 4. 归还检查清单

#### 设备清理
- [ ] 删除个人账号信息
- [ ] 卸载测试应用
- [ ] 清理测试数据
- [ ] 恢复系统设置

#### 硬件检查
- [ ] 屏幕显示正常
- [ ] 按键功能正常
- [ ] 充电接口正常
- [ ] 网络连接正常

#### 配件检查
- [ ] 充电器
- [ ] 数据线
- [ ] 保护套/膜
- [ ] 其他配件

### 5. 归还说明

#### 归还原因示例
- "测试完成"
- "项目结束"
- "功能验证完毕"
- "临时使用结束"

#### 特殊情况说明
- 如有设备问题，详细描述
- 如有配件缺失，及时说明
- 如需继续使用，重新申请

### 6. 相关工具

#### 仅记录操作
如果只需要添加归还记录而不更新设备状态：
```
add_return_record(asset_number, borrower, reason)
```

#### 查询归还记录
```
get_device_records(record_type="归还")
```

### 7. 故障排除

#### 归还失败原因
- 资产编号不存在
- 设备未被借用
- 归还者与借用者不匹配
- 参数格式错误

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    return types.GetPromptResult(
        description="设备归还流程指导",
        messages=[
            types.PromptMessage(
                role="user",
                content=types.TextContent(type="text", text=prompt_content)
            )
        ]
    )


async def _handle_windows_architecture_guide_prompt(arguments: dict[str, str]) -> types.GetPromptResult:
    """处理Windows设备架构查询指导提示"""
    target_arch = arguments.get("target_arch", "x64")
    
    prompt_content = f"""
# Windows设备架构查询指导

## 目标架构: {target_arch}

## 架构查询功能

### 1. 获取所有架构
使用 `get_windows_architectures` 工具：
```
get_windows_architectures()
```

#### 返回结果
- 列出所有可用的芯片架构
- 按字母顺序排序
- 显示架构统计信息

### 2. 按架构查询设备
使用 `query_devices_by_architecture` 工具：
```
query_devices_by_architecture(architecture="{target_arch}")
```

#### 查询范围
- 仅限Windows设备
- 精确匹配架构名称
- 返回详细设备信息

### 3. 支持的架构类型

#### x64架构
- 64位Intel/AMD处理器
- 兼容性最广
- 性能优秀
- 常见于台式机和笔记本

#### arm64架构  
- 64位ARM处理器
- 低功耗设计
- 续航优秀
- 常见于Surface Pro X等

### 4. 架构查询应用场景

#### 开发测试
- 应用兼容性测试
- 性能对比测试
- 架构特定功能验证

#### 设备选择
- 根据项目需求选择合适架构
- 考虑应用兼容性要求
- 评估性能需求

### 5. 查询结果信息

#### 设备详情
- 设备名称和型号
- 芯片架构信息
- 设备状态
- 借用者信息
- 资产编号

#### 统计信息
- 总设备数量
- 可用设备数量
- 使用中设备数量
- 架构分布情况

### 6. 架构选择建议

#### x64架构适用
- 通用应用开发
- 高性能计算需求
- 兼容性测试
- 企业级应用

#### arm64架构适用
- 移动应用适配
- 低功耗测试
- 续航性能测试
- 新架构兼容性

### 7. 相关操作

#### 设备借用
找到合适架构设备后：
```
borrow_device(asset_number, borrower, reason)
```

#### 设备信息
获取设备详细信息：
```
get_device_info(device_id, device_type="windows")
```

### 8. 注意事项

#### 架构兼容性
- 确认应用支持目标架构
- 注意架构特定的限制
- 考虑性能差异

#### 设备可用性
- 优先选择可用设备
- 考虑设备配置差异
- 确认设备状态正常

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    return types.GetPromptResult(
        description="Windows设备架构查询指导",
        messages=[
            types.PromptMessage(
                role="user",
                content=types.TextContent(type="text", text=prompt_content)
            )
        ]
    )


async def _handle_device_records_analysis_prompt(arguments: dict[str, str]) -> types.GetPromptResult:
    """处理设备记录分析模板提示"""
    analysis_type = arguments.get("analysis_type", "usage")
    time_period = arguments.get("time_period", "weekly")
    
    prompt_content = f"""
# 设备记录分析模板

## 分析类型: {analysis_type}
## 时间范围: {time_period}

## 数据获取

### 1. 获取记录数据
使用 `get_device_records` 工具：
```
get_device_records(record_type="all")
```

#### 记录类型
- **all**: 所有借用和归还记录
- **借用**: 仅借用记录
- **归还**: 仅归还记录

### 2. 分析维度

#### 使用分析 (usage)
- 设备使用频率统计
- 热门设备排行
- 使用时长分析
- 设备利用率计算

#### 趋势分析 (trends)
- 借用归还趋势
- 季节性使用模式
- 设备类型偏好变化
- 用户行为模式

#### 问题分析 (issues)
- 设备故障记录
- 异常使用模式
- 逾期未归还统计
- 设备维护需求

### 3. 分析指标

#### 基础指标
- 总借用次数
- 总归还次数
- 平均使用时长
- 设备周转率

#### 设备维度
- 设备类型使用分布
- 热门设备TOP10
- 设备故障率
- 设备空闲率

#### 用户维度
- 活跃用户统计
- 用户使用偏好
- 部门使用情况
- 使用时长分布

### 4. 时间周期分析

#### 每日分析 (daily)
- 当日借用归还情况
- 实时设备状态
- 当日异常记录

#### 每周分析 (weekly)
- 周度使用趋势
- 工作日vs周末使用
- 周度设备周转

#### 每月分析 (monthly)
- 月度使用报告
- 设备采购建议
- 用户满意度评估

### 5. 分析报告模板

#### 执行摘要
- 关键指标总结
- 主要发现
- 改进建议

#### 详细分析
- 数据图表展示
- 趋势变化说明
- 异常情况分析

#### 行动建议
- 设备采购建议
- 流程优化建议
- 用户培训需求

### 6. 常用分析查询

#### 借用频率分析
```
# 获取所有借用记录
get_device_records(record_type="借用")

# 分析最常借用的设备
# 统计借用频次
# 计算平均使用时长
```

#### 设备利用率分析
```
# 获取设备列表
list_devices(device_type="all", status="all")

# 获取使用记录
get_device_records(record_type="all")

# 计算利用率 = 使用时间 / 总时间
```

### 7. 数据可视化建议

#### 图表类型
- 柱状图：设备类型使用分布
- 折线图：使用趋势变化
- 饼图：设备状态分布
- 热力图：使用时间分布

#### 关键指标仪表板
- 实时可用设备数
- 当前借用率
- 平均使用时长
- 设备故障率

### 8. 改进建议输出

#### 设备管理
- 增减设备建议
- 设备配置优化
- 维护计划调整

#### 流程优化
- 借用流程改进
- 归还提醒机制
- 用户体验提升

生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    return types.GetPromptResult(
        description="设备记录分析模板",
        messages=[
            types.PromptMessage(
                role="user",
                content=types.TextContent(type="text", text=prompt_content)
            )
        ]
    )


if __name__ == "__main__":
    main()
