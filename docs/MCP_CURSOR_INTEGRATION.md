# MCP Cursor 集成说明

## 集成完成

您的MCP服务器已成功集成到Cursor中，使用HTTP Stream方式连接。

## 配置详情

### 1. Cursor MCP 配置 (`~/.cursor/mcp.json`)
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

### 2. 项目规则更新 (`.cursorrules`)
- 明确声明仅支持HTTP Stream集成方式
- 添加了MCP集成的使用流程
- 更新了服务器特性说明
- 包含了详细的开发规则

## 使用步骤

### 启动MCP服务器
```bash
# 方式1: 使用启动脚本
scripts\run_fastmcp_server.bat

# 方式2: 直接运行Python文件
python src\mcp_server\fastmcp_test_server.py
```

### 验证服务器运行
服务器启动后应该显示：
```
============================================================
Simple MCP测试服务器
============================================================
name: Simple MCP Test Server
version: 1.0.0
transport: HTTP
tools: ['test_tool']
prompts: ['test_prompt']
status: running
============================================================
服务器地址: http://localhost:8001
MCP端点: /mcp
按 Ctrl+C 停止服务器
============================================================
```

### 在Cursor中使用MCP
1. **确保MCP服务器正在运行**
2. **重启Cursor** (如果需要重新加载mcp.json配置)
3. **使用MCP工具和提示**:
   - Cursor将自动检测到TestDeviceManagement MCP服务器
   - 可以使用 `test_tool` 工具
   - 可以使用 `test_prompt` 提示

## 可用的MCP功能

### 🔧 工具 (Tools)
- **test_tool**: 测试工具
  - **功能**: 接收消息并返回带时间戳的确认
  - **参数**: `message` (字符串, 可选)
  - **示例**: 发送"Hello MCP"消息测试连接

### 💬 提示 (Prompts)  
- **test_prompt**: 测试提示
  - **功能**: 生成基于主题和上下文的提示内容
  - **参数**: 
    - `topic` (字符串, 可选) - 提示主题
    - `context` (字符串, 可选) - 上下文信息
  - **返回**: Markdown格式的提示内容

## 调试和监控

### 服务器日志
MCP服务器会输出详细的日志信息：
- `[MCP] 收到请求`: 显示从Cursor接收到的请求
- `[MCP] 发送响应`: 显示发送给Cursor的响应
- `[测试工具] 处理消息`: 工具调用日志
- `[测试提示] 生成提示`: 提示生成日志

### 手动测试
可以使用测试客户端验证MCP服务器：
```bash
scripts\test_fastmcp_client.bat
```

## 故障排查

### 常见问题
1. **Cursor无法连接到MCP服务器**
   - 确保MCP服务器正在运行
   - 检查端口8001是否被占用
   - 验证URL配置是否正确: `http://localhost:8001/mcp`

2. **MCP配置未生效**
   - 重启Cursor应用
   - 检查mcp.json文件格式是否正确
   - 确认文件路径: `~/.cursor/mcp.json`

3. **工具或提示不可用**
   - 检查服务器日志是否有错误
   - 确认工具和提示已正确注册
   - 验证JSON-RPC请求格式

### 日志示例
正常工作时的服务器日志：
```
2024-01-01 12:00:00 - __main__ - INFO - [MCP] 收到请求: {"jsonrpc": "2.0", "id": 1, "method": "tools/list"}
2024-01-01 12:00:00 - __main__ - INFO - [MCP] 发送响应: {"jsonrpc": "2.0", "id": 1, "result": {"tools": [...]}}
```

## 集成特点

- ✅ **HTTP Stream**: 使用标准HTTP协议，无需WebSocket或stdio
- ✅ **手动启动**: 服务器需要手动启动，便于调试和控制
- ✅ **详细日志**: 完整的MCP交互日志，便于开发调试
- ✅ **标准协议**: 严格遵循MCP 2024-11-05规范
- ✅ **易于扩展**: 可以轻松添加新的工具和提示

## 下一步开发

1. **添加更多工具**: 在服务器中添加设备管理相关的工具
2. **集成设备功能**: 将现有的设备管理代码集成到MCP工具中
3. **增强提示**: 添加更多有用的提示模板
4. **错误处理**: 改善错误处理和用户体验

您的MCP服务器现在已经完全集成到Cursor中，可以开始使用和开发了！
