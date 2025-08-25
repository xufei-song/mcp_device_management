# MCP协议传输方式对比：SSE vs Streamable HTTP

## 概述
MCP (Model Context Protocol) 支持多种传输方式，其中SSE (Server-Sent Events) 和 Streamable HTTP 是两种重要的流式传输模式。

## SSE (Server-Sent Events) 传输模式

### 特点
- **单向流式通信**：服务器向客户端推送实时数据流
- **基于HTTP/1.1**：使用标准HTTP连接，但保持长连接
- **事件驱动**：支持命名事件类型，客户端可监听特定事件
- **自动重连**：浏览器原生支持断线重连机制
- **文本格式**：数据以文本形式传输，通常是JSON

### 技术实现
```
GET /mcp/sse HTTP/1.1
Accept: text/event-stream
Cache-Control: no-cache

服务器响应：
data: {"type": "tool_result", "content": "..."}

data: {"type": "progress", "percentage": 50}

data: {"type": "completed"}
```

### 适用场景
- **实时状态更新**：设备状态变化、进度报告
- **通知推送**：系统事件、错误警告
- **流式响应**：大型数据集的分批传输
- **监控面板**：实时数据展示

## Streamable HTTP 传输模式

### 特点
- **双向通信**：支持请求-响应和流式响应
- **HTTP/2兼容**：更好的多路复用和头部压缩
- **分块传输**：使用HTTP chunked encoding
- **灵活格式**：支持多种数据格式（JSON、二进制等）
- **流控制**：更精细的流量控制机制

### 技术实现
```
POST /mcp/stream HTTP/1.1
Transfer-Encoding: chunked
Content-Type: application/json

请求体分块传输：
{"method": "tool_call", "stream": true}

响应流式返回：
{"partial_result": "chunk1"}
{"partial_result": "chunk2"}
{"final_result": "complete"}
```

### 适用场景
- **大文件传输**：设备文件上传/下载
- **流式处理**：实时数据处理管道
- **批量操作**：多设备批量管理
- **API调用**：复杂的工具调用链

## 主要区别对比

| 特性 | SSE | Streamable HTTP |
|------|-----|-----------------|
| **通信方向** | 单向（服务器→客户端） | 双向（请求/响应流） |
| **连接模式** | 长连接 | 请求-响应周期 |
| **数据格式** | 文本流（通常JSON） | 多格式（JSON/二进制） |
| **重连机制** | 浏览器原生支持 | 需手动实现 |
| **流控制** | 基础 | 高级（HTTP/2） |
| **复杂度** | 简单 | 中等 |
| **性能** | 适中 | 更高（HTTP/2） |
| **兼容性** | 广泛支持 | 需要现代浏览器 |

## 在MCP设备管理系统中的应用

### SSE使用场景
```javascript
// 监听设备状态变化
const eventSource = new EventSource('/mcp/sse/device-status');
eventSource.onmessage = function(event) {
    const deviceUpdate = JSON.parse(event.data);
    updateDeviceUI(deviceUpdate);
};
```

### Streamable HTTP使用场景
```javascript
// 流式上传设备文件
const response = await fetch('/mcp/stream/upload', {
    method: 'POST',
    body: fileStream,
    headers: {'Transfer-Encoding': 'chunked'}
});

// 处理流式响应
const reader = response.body.getReader();
while (true) {
    const {done, value} = await reader.read();
    if (done) break;
    processChunk(value);
}
```

## 选择建议

### 选择SSE的情况
- 需要实时推送设备状态
- 简单的单向数据流
- 浏览器兼容性要求高
- 开发复杂度要求低

### 选择Streamable HTTP的情况
- 需要大文件传输
- 复杂的双向交互
- 性能要求高
- 支持HTTP/2环境

## 实施注意事项

### SSE注意事项
- 浏览器连接数限制（通常6个）
- 需要处理CORS跨域问题
- 服务器需要定期发送心跳

### Streamable HTTP注意事项
- 需要实现错误重试机制
- 流控制和背压处理
- 内存管理（避免缓冲区溢出）

## 结论
SSE和Streamable HTTP各有优势，在MCP设备管理系统中可以根据具体需求选择合适的传输方式。对于实时状态监控，SSE更简单有效；对于文件传输和复杂交互，Streamable HTTP更强大灵活。在实际项目中，两种方式可以并存，为不同场景提供最优的用户体验。
