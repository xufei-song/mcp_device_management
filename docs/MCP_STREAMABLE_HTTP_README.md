# MCP Streamable HTTP 服务器

基于 MCP 规范 2025-06-18 实现的最简单的 Streamable HTTP MCP 服务器。

## 功能特性

### 核心功能
- ✅ **Streamable HTTP 传输协议** - 支持 HTTP POST 和 GET 请求
- ✅ **会话管理** - 自动生成和管理会话 ID
- ✅ **安全验证** - Origin 头验证，防止 DNS 重绑定攻击
- ✅ **协议版本支持** - 支持 MCP 协议版本 2025-06-18
- ✅ **青色调试输出** - 所有操作都有青色日志输出，便于调试

### 工具和提示
- ✅ **2个固定工具**:
  - `simple_tool_1`: 接收消息并返回确认
  - `simple_tool_2`: 接收数字并返回平方结果
- ✅ **2个固定提示**:
  - `simple_prompt_1`: 主题相关提示
  - `simple_prompt_2`: 问题相关提示

### 支持的 MCP 方法
- ✅ `initialize` - 初始化连接
- ✅ `tools/list` - 获取工具列表
- ✅ `tools/call` - 调用工具
- ✅ `prompts/list` - 获取提示列表

## 快速开始

### 1. 启动服务器

```bash
# 方法1: 使用批处理脚本（推荐）
scripts\run_mcp_streamable_http.bat

# 方法2: 直接运行
python src\mcp\streamable_http_server.py
```

服务器将在 `http://127.0.0.1:8000` 启动。

### 2. 测试服务器

```bash
# 使用测试客户端
scripts\test_mcp_server.bat
```

### 3. 手动测试

#### 初始化连接
```bash
curl -X POST http://127.0.0.1:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "MCP-Protocol-Version: 2025-06-18" \
  -d '{
    "jsonrpc": "2.0",
    "id": "1",
    "method": "initialize",
    "params": {
      "protocolVersion": "2025-06-18",
      "capabilities": {},
      "clientInfo": {
        "name": "TestClient",
        "version": "1.0.0"
      }
    }
  }'
```

#### 获取工具列表
```bash
curl -X POST http://127.0.0.1:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "MCP-Protocol-Version: 2025-06-18" \
  -H "MCP-Session-Id: YOUR_SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "id": "2",
    "method": "tools/list"
  }'
```

#### 调用工具
```bash
curl -X POST http://127.0.0.1:8000/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "MCP-Protocol-Version: 2025-06-18" \
  -H "MCP-Session-Id: YOUR_SESSION_ID" \
  -d '{
    "jsonrpc": "2.0",
    "id": "3",
    "method": "tools/call",
    "params": {
      "name": "simple_tool_1",
      "arguments": {
        "message": "你好，世界！"
      }
    }
  }'
```

## 服务器端点

### POST /mcp
处理所有 MCP 请求，包括：
- 初始化
- 工具列表
- 工具调用
- 提示列表

### GET /mcp
建立 SSE (Server-Sent Events) 流，用于：
- 服务器到客户端的通知
- 心跳保持
- 实时事件推送

## 安全特性

### Origin 验证
服务器验证 `Origin` 头，只允许来自以下来源的请求：
- `http://localhost:3000`
- `http://127.0.0.1:3000`

### 本地绑定
服务器只绑定到 `127.0.0.1`，不暴露到外部网络。

### 会话管理
- 自动生成安全的会话 ID
- 会话验证和过期处理
- 支持会话终止

## 调试功能

### 青色日志输出
所有服务器操作都会以青色输出到控制台，包括：
- 请求接收
- 方法处理
- 工具调用
- 错误信息

### 详细日志
- 请求和响应内容
- 会话 ID 跟踪
- 错误详情

## 依赖项

### 核心依赖
- `fastapi` - Web 框架
- `uvicorn` - ASGI 服务器
- `sse-starlette` - SSE 支持
- `aiohttp` - 异步 HTTP 客户端（测试用）

### 安装依赖
```bash
pip install fastapi uvicorn sse-starlette aiohttp
```

## 文件结构

```
src/mcp/
├── __init__.py                    # 包初始化
├── streamable_http_server.py      # 主服务器实现
└── test_client.py                 # 测试客户端

scripts/
├── run_mcp_streamable_http.bat    # 启动脚本
└── test_mcp_server.bat            # 测试脚本
```

## 扩展开发

### 添加新工具
在 `StreamableHTTPMCPServer` 类的 `__init__` 方法中添加工具定义：

```python
self.tools.append({
    "name": "new_tool",
    "description": "新工具描述",
    "inputSchema": {
        "type": "object",
        "properties": {
            "param": {"type": "string"}
        },
        "required": ["param"]
    }
})
```

### 添加工具处理逻辑
在 `handle_tools_call` 方法中添加处理逻辑：

```python
elif tool_name == "new_tool":
    param = arguments.get("param", "")
    result = {
        "content": [
            {
                "type": "text",
                "text": f"新工具结果: {param}"
            }
        ]
    }
```

## 故障排除

### 常见问题

1. **端口被占用**
   - 修改 `streamable_http_server.py` 中的端口号
   - 或停止占用端口的其他服务

2. **依赖安装失败**
   - 确保使用正确的 Python 版本 (3.8+)
   - 检查网络连接
   - 尝试使用国内镜像源

3. **CORS 错误**
   - 检查 Origin 头设置
   - 确保客户端来自允许的域名

4. **会话 ID 无效**
   - 确保先调用 `initialize` 方法
   - 检查会话 ID 是否正确传递

### 调试技巧

1. **查看详细日志**
   - 服务器启动时会显示青色调试信息
   - 所有请求和响应都会记录

2. **使用测试客户端**
   - 运行 `test_mcp_server.bat` 进行完整测试
   - 检查每个步骤的输出

3. **检查网络连接**
   - 使用 `curl` 或浏览器测试端点
   - 确认服务器正在监听正确的端口

## 规范遵循

本实现严格遵循 [MCP 规范 2025-06-18](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports)：

- ✅ JSON-RPC 2.0 消息格式
- ✅ Streamable HTTP 传输协议
- ✅ 会话管理
- ✅ 安全最佳实践
- ✅ 错误处理
- ✅ 协议版本协商
