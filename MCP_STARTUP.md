# MCP服务器启动说明

## 🚀 快速启动

### 1. 启动MCP服务器

```bash
# 方式1: 使用Python脚本
python run_mcp_server.py

# 方式2: 使用uvicorn直接启动
uvicorn src.main:app --host localhost --port 8000 --reload

# 方式3: 使用Windows脚本
scripts\run_dev.bat
```

### 2. 验证服务状态

服务器启动后，您可以通过以下方式验证：

- **HTTP API**: http://localhost:8000/docs
- **MCP WebSocket**: ws://localhost:8000/mcp
- **健康检查**: http://localhost:8000/health

## 🔧 MCP协议测试

### 使用测试脚本

```bash
# 安装依赖
pip install websockets requests

# 运行测试
python test_mcp_client.py
```

### 手动测试WebSocket

使用WebSocket客户端连接到 `ws://localhost:8000/mcp`，发送以下消息：

#### 初始化
```json
{
  "id": "init_1",
  "type": "initialize"
}
```

#### 获取工具列表
```json
{
  "id": "tools_1",
  "type": "tools/list"
}
```

#### 调用工具
```json
{
  "id": "call_1",
  "type": "tools/call",
  "name": "device.list",
  "arguments": {}
}
```

#### 获取资源列表
```json
{
  "id": "resources_1",
  "type": "resources/list",
  "uri": "mcp://test-devices/"
}
```

## 📡 支持的MCP消息类型

### 核心消息
- `initialize` - 协议初始化
- `tools/list` - 获取可用工具列表
- `tools/call` - 调用指定工具
- `resources/list` - 获取资源列表
- `resources/read` - 读取指定资源

### 扩展消息
- `resources/watch` - 监听资源变化
- `resources/unwatch` - 取消资源监听
- `prompts/list` - 获取提示列表
- `prompts/create` - 创建提示
- `prompts/update` - 更新提示
- `prompts/delete` - 删除提示

## 🌐 双重接口支持

### HTTP API
- 端点: `/api/*`
- 文档: `/docs`
- 适合: 传统REST客户端

### MCP协议
- 端点: `/mcp` (WebSocket)
- 协议: MCP 2024-11-05
- 适合: AI Agent、MCP客户端

## 🔍 故障排除

### 常见问题

1. **端口被占用**
   ```bash
   # 查找占用端口的进程
   netstat -ano | findstr :8000
   
   # 终止进程
   taskkill /PID <进程ID> /F
   ```

2. **依赖缺失**
   ```bash
   # 安装所有依赖
   pip install -r requirements.txt
   
   # 或者安装开发依赖
   pip install -e ".[dev]"
   ```

3. **WebSocket连接失败**
   - 检查服务器是否启动
   - 确认WebSocket端点 `/mcp` 可用
   - 检查防火墙设置

### 日志查看

服务器运行时会输出以下日志：
- `[MCP] 新连接建立，当前连接数: X`
- `[MCP] 连接断开，当前连接数: X`
- `[MCP] 发送消息失败: <错误信息>`

## 📚 相关文档

- [MCP API文档](docs/MCP_API.md) - 完整的API接口说明
- [快速开始指南](QUICKSTART.md) - 项目设置和使用说明
- [开发指导](.cursorrules) - 详细的开发文档

## 🎯 下一步

1. 启动服务器并测试MCP协议
2. 使用测试脚本验证功能
3. 集成到您的AI Agent或MCP客户端
4. 根据需要扩展更多MCP功能

---

**注意**: 确保在运行MCP服务器之前已经完成了环境设置和依赖安装。
