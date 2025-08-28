# Test Device Management MCP

## 项目概述

这是一个基于MCP（Model Context Protocol）的测试设备管理系统，用于管理和监控不同类型的测试设备，包括Android、iOS和Windows设备。

## 快速启动

```bash
# 1. 运行设置脚本（只需要运行一次）
scripts\setup.bat

# 2. 激活虚拟环境
scripts\activate.bat

# 3. 启动MCP服务器
scripts\run_fastmcp_server.bat
```

## 项目结构

```
TestDeviceManagmentMCP/
├── Devices/                    # 设备目录
│   ├── Android/               # Android设备
│   ├── IOS/                   # iOS设备
│   └── Windows/               # Windows设备
├── src/                       # 源代码目录
│   ├── mcp_server/            # MCP服务器实现
│   ├── device/                # 设备管理核心
│   ├── handlers/              # 请求处理器
│   └── utils/                 # 工具函数
├── scripts/                   # 启动脚本
├── config/                    # 配置文件
├── tests/                     # 测试文件
└── docs/                      # 文档
```

## MCP服务器特性

### 🔧 测试工具 (test_tool)
- **功能**: 接收消息并返回带时间戳的确认响应
- **参数**: `message` (字符串) - 测试消息内容
- **返回**: JSON格式的响应，包含状态、消息、时间戳和服务器信息

### 💬 测试提示 (test_prompt)
- **功能**: 根据主题和上下文生成测试提示内容
- **参数**: 
  - `topic` (字符串) - 提示主题
  - `context` (字符串) - 上下文信息
- **返回**: Markdown格式的提示内容

### 🌐 HTTP Stream 支持
- 支持标准的MCP HTTP协议
- 基于FastAPI和uvicorn构建
- 默认运行在 `localhost:8001`
- 详细的调试输出，便于开发调试

## Cursor集成

本项目已集成到Cursor中，使用HTTP Stream方式：

### MCP配置 (`~/.cursor/mcp.json`)
```json
{
  "mcpServers": {
    "TestDeviceManagement": {
      "url": "http://localhost:8001/mcp",
      "description": "测试设备管理MCP服务器 - HTTP Stream方式连接"
    }
  }
}
```

### 使用流程
1. 启动MCP服务器: `scripts\run_fastmcp_server.bat`
2. 确认服务器运行在 http://localhost:8001
3. 在Cursor中直接使用MCP工具和提示
4. 查看服务器日志了解MCP交互情况

## 核心功能设计

### 1. 设备管理
- **设备注册**: 自动发现和注册新设备
- **设备分类**: 按类型（Android/iOS/Windows）组织设备
- **设备状态**: 实时监控设备状态（在线/离线/忙碌/空闲）
- **设备信息**: 存储设备详细信息（型号、版本、能力等）

### 2. MCP协议实现
- **HTTP Stream**: 仅支持HTTP Stream集成方式
- **工具调用**: 提供设备操作工具
- **提示生成**: 基于上下文的智能提示
- **详细日志**: 所有MCP操作都有详细日志输出

### 3. 设备操作
- **连接管理**: 建立/断开设备连接
- **命令执行**: 在设备上执行测试命令
- **文件传输**: 上传/下载测试文件
- **日志收集**: 收集设备运行日志

## 技术架构

### 后端技术栈
- **语言**: Python 3.8+
- **框架**: FastAPI (用于MCP服务器)
- **数据库**: SQLite/PostgreSQL (设备信息存储)
- **通信**: HTTP (MCP协议), WebSocket (实时状态更新)
- **序列化**: JSON/YAML (配置文件)

### 依赖包
- fastapi: Web框架
- uvicorn: ASGI服务器
- aiohttp: 异步HTTP客户端
- pyyaml: YAML配置文件支持
- python-dotenv: 环境变量管理

## 手动测试MCP接口

### 工具调用示例
```bash
curl -X POST http://localhost:8001/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "test_tool",
      "arguments": {
        "message": "Hello MCP"
      }
    }
  }'
```

### 提示调用示例
```bash
curl -X POST http://localhost:8001/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "prompts/get",
    "params": {
      "name": "test_prompt",
      "arguments": {
        "topic": "设备管理",
        "context": "测试环境"
      }
    }
  }'
```

## 开发扩展

### 添加新工具
在 `src/mcp_server/fastmcp_test_server.py` 中添加:

```python
async def new_tool_handler(param: str) -> str:
    # 工具实现
    return "result"

mcp_server.add_tool(
    name="new_tool",
    description="新工具描述",
    input_schema={
        "type": "object",
        "properties": {
            "param": {"type": "string", "description": "参数描述"}
        }
    },
    handler=new_tool_handler
)
```

### 添加新提示
在 `src/mcp_server/fastmcp_test_server.py` 中添加:

```python
async def new_prompt_handler(param: str) -> str:
    # 提示实现
    return "prompt content"

mcp_server.add_prompt(
    name="new_prompt",
    description="新提示描述",
    arguments=[
        {"name": "param", "description": "参数描述", "required": False}
    ],
    handler=new_prompt_handler
)
```

## 故障排查

### 常见问题

1. **依赖包未安装**
   ```bash
   pip install fastapi uvicorn aiohttp
   ```

2. **端口被占用**
   - 修改 `fastmcp_test_server.py` 中的端口号
   - 或者设置环境变量 `FASTMCP_PORT`

3. **Cursor无法连接到MCP服务器**
   - 确保MCP服务器正在运行
   - 检查端口8001是否被占用
   - 验证URL配置是否正确: `http://localhost:8001/mcp`

### 日志调试
服务器运行时会输出详细调试信息，包括:
- MCP请求/响应日志
- 工具调用日志
- 提示生成日志
- 错误信息
- 服务器状态

## 开发规则

- **仅HTTP传输**: 本工程只考虑HTTP Stream集成方式
- **手动启动**: MCP服务器需要手动启动，不在mcp.json中配置自动启动
- **扩展开发**: 新增工具和提示都通过add_tool/add_prompt方法添加
- **日志优先**: 所有操作都要有详细的日志输出

## 设备资源URI格式

```
mcp://test-devices/devices/{device_type}/{device_id}
mcp://test-devices/devices/android/emulator-5554
mcp://test-devices/devices/ios/00008120-001C25D40C0A002E
mcp://test-devices/devices/windows/DESKTOP-ABC123
```

## 核心工具列表（计划实现）

1. **device.list** - 列出所有设备
2. **device.connect** - 连接设备
3. **device.disconnect** - 断开设备
4. **device.execute** - 执行命令
5. **device.upload** - 上传文件
6. **device.download** - 下载文件
7. **device.status** - 获取设备状态

## 环境变量配置

```bash
# .env
MCP_SERVER_HOST=localhost
MCP_SERVER_PORT=8001
DEVICE_DISCOVERY_INTERVAL=30
LOG_LEVEL=INFO
```

## 规范遵循

严格遵循 MCP 规范 2024-11-05，包括JSON-RPC 2.0消息格式、HTTP传输协议等。

## 许可证

本项目遵循项目根目录的许可证条款。

---

**注意**: 这是一个开发指导文档，在实际开发过程中可能需要根据具体需求和环境进行调整。