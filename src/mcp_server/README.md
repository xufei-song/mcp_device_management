# MCP 测试服务器

这是一个基于标准MCP协议实现的测试服务器，支持HTTP接口。使用FastAPI和uvicorn构建，无需依赖第三方FastMCP库。

## 文件结构

```
src/mcp_server/
├── __init__.py                 # 包初始化文件
├── fastmcp_test_server.py     # MCP测试服务器主文件
├── test_fastmcp_client.py     # 测试客户端
└── README.md                  # 使用说明
```

## 功能特性

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

### 🌐 HTTP 支持
- 支持标准的MCP HTTP协议
- 基于FastAPI和uvicorn构建
- 默认运行在 `localhost:8001`
- 详细的调试输出，便于开发调试

## 快速开始

### 1. 启动服务器
```bash
# Windows
scripts\run_fastmcp_server.bat

# 或者直接运行Python文件
python src\mcp_server\fastmcp_test_server.py
```

### 2. 测试客户端
```bash
# Windows
scripts\test_fastmcp_client.bat

# 或者直接运行Python文件
python src\mcp_server\test_fastmcp_client.py
```

### 3. 手动测试

#### 工具调用示例
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
        "message": "Hello FastMCP"
      }
    }
  }'
```

#### 提示调用示例
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

## 配置说明

### 服务器配置
- **主机**: localhost
- **端口**: 8001
- **传输协议**: HTTP Stream
- **日志级别**: INFO

### 环境变量
- `FASTMCP_HOST`: 服务器主机地址 (默认: localhost)
- `FASTMCP_PORT`: 服务器端口 (默认: 8001)
- `LOG_LEVEL`: 日志级别 (默认: INFO)

## 开发说明

### 添加新工具
在 `fastmcp_test_server.py` 中添加:

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
在 `fastmcp_test_server.py` 中添加:

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

3. **连接失败**
   - 确保服务器已启动
   - 检查防火墙设置
   - 验证端口是否正确

### 日志调试
服务器运行时会输出详细调试信息，包括:
- MCP请求/响应日志
- 工具调用日志
- 提示生成日志
- 错误信息
- 服务器状态

## 扩展开发

这个测试服务器可以作为基础，扩展为更复杂的MCP服务器:

1. **设备管理工具**: 集成真实的设备管理功能
2. **数据库集成**: 添加持久化存储
3. **认证授权**: 添加安全验证
4. **监控指标**: 添加性能监控
5. **配置管理**: 支持动态配置

## 许可证

本项目遵循项目根目录的许可证条款。
