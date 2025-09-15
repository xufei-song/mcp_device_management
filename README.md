# Test Device Management MCP

## 项目概述

这是一个基于MCP（Model Context Protocol）的测试设备管理系统，用于管理和监控测试设备，记录设备信息（SKU、序列号、借用状态等）。

## 快速启动

```bash
# 1. 运行设置脚本（只需要运行一次）
scripts\setup.bat

# 2. 激活虚拟环境
scripts\activate.bat

# 3. 启动MCP服务器
scripts\run_mcp_server2.bat
```

## 项目结构

```
TestDeviceManagmentMCP/
├── Devices/                    # 设备数据目录
│   ├── test_devices.xlsx     # 设备清单XLSX文件（主数据源）
│   └── backup/               # 历史备份文件
├── src/                       # 源代码目录
│   ├── mcp_server2/           # MCP服务器实现
│   │   ├── server.py          # 主服务器实现
│   │   ├── event_store.py     # 事件存储
│   │   └── __main__.py        # 模块入口
│   ├── device/                # 设备管理核心
│   └── utils/                 # 工具函数
├── scripts/                   # 启动脚本
└── docs/                      # 文档
```

## MCP服务器特性

### 🔧 设备管理工具
- **get_device_info**: 获取设备详细信息（SKU、序列号、状态等）
- **list_devices**: 列出所有可用设备
- **borrow_device**: 借用设备
- **return_device**: 归还设备
- **update_device_status**: 更新设备状态

### 💬 智能提示系统
- **device_test_plan**: 生成设备测试计划模板
- **bug_report_template**: 生成Bug报告模板

### 🌐 传输协议
- **协议**: HTTP Stream (MCP标准)
- **端口**: 8002
- **特点**: 实时通知、断点续传、会话管理

## Cursor集成

本项目已集成到Cursor中，使用HTTP Stream方式：

### MCP配置 (`~/.cursor/mcp.json`)
```json
{
  "mcpServers": {
    "DeviceManagement": {
      "url": "http://127.0.0.1:8002/mcp",
      "transport": "http-stream",
      "description": "测试设备管理MCP服务器"
    }
  }
}
```

### 使用流程
1. 启动MCP服务器: `scripts\run_mcp_server2.bat`
2. 确认服务器运行在 http://127.0.0.1:8002
3. 在Cursor中使用 `DeviceManagement` 服务器

## 核心功能设计

### 1. 设备管理
- **XLSX数据存储**: 使用Excel XLSX格式存储所有设备信息，支持丰富的数据格式和验证
- **设备信息**: 记录设备基本信息（SKU、序列号、型号、品牌等）
- **状态跟踪**: 跟踪设备状态（可用/正在使用/维护中/报废）
- **借用记录**: 记录借用者、所属manager、借用时间等信息
- **数据完整性**: XLSX格式支持数据验证、格式化和复杂的工作表结构

### 2. MCP协议实现
- **HTTP Stream**: 使用官方MCP Python SDK
- **实时通知**: 设备状态变更时实时通知
- **会话管理**: 自动管理连接生命周期

### 3. 设备操作
- **借用管理**: 借用/归还设备
- **状态更新**: 更新设备状态和位置
- **信息查询**: 查询设备详细信息和借用历史

## 数据存储格式

### XLSX设备数据结构
设备数据统一存储在 `Devices/test_devices.xlsx` 文件中，包含以下字段：

| 字段名称 | 描述 | 示例值 |
|---------|------|--------|
| 创建日期 | 设备录入系统的日期 | 2023.11.28 |
| 设备名称 | 设备的完整名称 | SAMSUNG Galaxy S24 |
| 设备OS | 设备操作系统 | Android |
| SKU | 设备型号/配置信息 | 8GB+256GB 星河白 |
| 类型 | 设备类别 | 手机/平板/Chromebook/Quest |
| 品牌 | 设备品牌 | Samsung/Pixel/Honor |
| 借用者 | 当前借用人 | vendor(Jayce) |
| 所属manager | 设备负责人 | Gary |
| 设备序列号 | 设备唯一标识 | RFCX10L1TZR |
| 资产编号 | 公司资产编号 | E2946640 |
| 是否盘点 | 盘点状态 | 是/否 |
| 设备状态 | 当前状态 | 可用/正在使用/维护中/报废 |

### XLSX格式优势
- **丰富格式**: 支持数据验证、条件格式、下拉列表等Excel功能
- **多工作表**: 可以分设备类型创建不同的工作表组织数据
- **数据完整性**: 内置数据验证确保数据质量和一致性
- **用户友好**: 非技术人员可以直接使用Excel查看和编辑
- **强大分析**: 支持Excel的透视表、图表、公式等分析功能
- **格式保留**: 保持单元格格式、颜色、注释等丰富信息

## 技术架构

### 后端技术栈
- **语言**: Python 3.8+
- **框架**: Starlette + 官方MCP Python SDK
- **数据存储**: XLSX文件格式（主数据源）
- **数据处理**: openpyxl/pandas处理Excel数据
- **通信**: HTTP Stream (MCP标准)
- **特性**: 实时通知、断点续传、会话管理

### 依赖包
- mcp: 官方MCP Python SDK
- starlette: ASGI框架
- uvicorn: ASGI服务器
- openpyxl: Excel文件读写操作
- pandas: 数据处理和分析
- anyio: 异步I/O支持
- click: 命令行接口

## 手动测试MCP接口

### 工具调用示例
```bash
curl -X POST http://127.0.0.1:8002/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "get_device_info",
      "arguments": {
        "device_id": "emulator-5554",
        "device_type": "android"
      }
    }
  }'
```

### 提示调用示例
```bash
curl -X POST http://127.0.0.1:8002/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "prompts/get",
    "params": {
      "name": "device_test_plan",
      "arguments": {
        "device_type": "android",
        "test_scope": "功能测试"
      }
    }
  }'
```

## 开发扩展

### 添加新工具
在 `src/mcp_server2/server.py` 中添加:

```python
@app.call_tool()
async def new_tool(name: str, arguments: dict[str, Any]) -> list[types.ContentBlock]:
    """新工具 - 使用SDK标准接口"""
    param = arguments.get("param")
    return [types.TextContent(type="text", text=f"结果: {param}")]

@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        # ... 现有工具 ...
        types.Tool(
            name="new_tool",
            description="新工具描述",
            inputSchema={
                "type": "object",
                "properties": {
                    "param": {"type": "string", "description": "参数描述"}
                }
            }
        )
    ]
```

### 添加新提示
在 `src/mcp_server2/server.py` 中添加:

```python
@app.get_prompt()
async def new_prompt(name: str, arguments: dict[str, str] | None = None) -> types.GetPromptResult:
    """新提示 - 使用SDK标准接口"""
    if name == "new_prompt":
        args = arguments or {}
        param = args.get("param", "默认值")
        content = f"# 新提示\n\n参数: {param}\n\n这是提示内容。"
        
        return types.GetPromptResult(
            description="新提示",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(type="text", text=content)
                )
            ]
        )
```

## 故障排查

### 常见问题

1. **依赖包未安装**
   ```bash
   pip install mcp starlette uvicorn openpyxl pandas
   ```

2. **端口被占用**
   - 修改 `src/mcp_server2/server.py` 中的端口号
   - 或者使用命令行参数 `--port 8003`

3. **Cursor无法连接到MCP服务器**
   - 确保MCP服务器正在运行
   - 检查端口8002是否被占用
   - 验证URL配置是否正确: `http://127.0.0.1:8002/mcp`

### 日志调试
服务器运行时会输出详细调试信息，包括:
- MCP请求/响应日志
- 工具调用日志
- 错误信息
- 服务器状态

## 开发规则

### 核心原则
- **HTTP Stream**: 使用官方MCP Python SDK实现HTTP Stream传输
- **手动启动**: MCP服务器需要手动启动，不在mcp.json中配置自动启动
- **扩展开发**: 使用SDK装饰器 `@app.call_tool()`, `@app.list_tools()` 等
- **日志优先**: 所有操作都要有详细的日志输出
- **设备管理**: 专注于设备信息记录和借用管理功能

## 设备资源URI格式

```
mcp://test-devices/devices/{device_type}/{device_id}
mcp://test-devices/devices/android/emulator-5554
mcp://test-devices/devices/ios/00008120-001C25D40C0A002E
mcp://test-devices/devices/windows/DESKTOP-ABC123
```

## 核心工具列表

### 已实现工具
1. **get_device_info** - 获取设备详细信息（SKU、序列号、状态等）
2. **list_devices** - 列出所有可用设备
3. **device_test_plan** - 生成设备测试计划模板
4. **bug_report_template** - 生成Bug报告模板

### 计划实现工具
1. **borrow_device** - 借用设备
2. **return_device** - 归还设备
3. **update_device_status** - 更新设备状态
4. **get_borrow_history** - 获取借用历史
5. **add_device** - 添加新设备
6. **remove_device** - 移除设备

## 环境变量配置

```bash
# .env
MCP_SERVER_HOST=127.0.0.1
MCP_SERVER_PORT=8002
LOG_LEVEL=INFO
```

## 规范遵循

### 协议标准
- 严格遵循 MCP 规范 2024-11-05
- 使用官方MCP Python SDK实现HTTP Stream传输
- 支持JSON-RPC 2.0消息格式

### 版本兼容性
- **协议版本**: 2024-11-05
- **传输方式**: HTTP Stream
- **SDK版本**: 最新官方MCP Python SDK
- **Python版本**: 3.8+

### 最佳实践
- 使用官方SDK确保协议兼容性
- 专注于设备管理核心功能
- 保持代码简洁和可维护性

## 许可证

本项目遵循项目根目录的许可证条款。

---

## 🎯 **总结**

### ✨ **项目亮点**
1. **专注设备管理**: 专门用于管理测试设备，记录SKU、序列号、借用状态等
2. **标准MCP实现**: 使用官方MCP Python SDK，完全符合MCP 2024-11-05规范
3. **HTTP Stream传输**: 支持实时通知和断点续传
4. **简洁架构**: 专注于核心功能，代码简洁易维护

### 🚀 **使用场景**
- **测试团队**: 管理测试设备的借用和归还
- **设备管理员**: 跟踪设备状态和位置
- **开发人员**: 快速查找可用设备

### 🔧 **技术优势**
- **协议标准**: 严格遵循MCP规范
- **代码质量**: 使用官方SDK，减少bug和维护成本
- **功能专注**: 专注于设备管理，功能清晰明确

---

**注意**: 这是一个开发指导文档，在实际开发过程中可能需要根据具体需求和环境进行调整。