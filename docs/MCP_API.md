# MCP测试设备管理系统 - API接口文档

## 📋 概述

本文档描述了MCP测试设备管理系统的所有API接口。系统基于MCP（Model Context Protocol）协议，提供设备管理、监控和操作的统一接口。

## 🌐 基础信息

- **协议**: MCP (Model Context Protocol) + HTTP REST
- **基础URI**: `mcp://test-devices/`
- **HTTP服务器**: `http://localhost:8000`
- **WebSocket**: `ws://localhost:8000/ws`
- **API文档**: `http://localhost:8000/docs`

## 📚 MCP协议接口

### 1. 资源管理 (Resources)

#### 1.1 资源URI格式

```
mcp://test-devices/devices/{device_type}/{device_id}
```

**参数说明：**
- `device_type`: 设备类型 (android|ios|windows)
- `device_id`: 设备唯一标识符

**示例：**
```
mcp://test-devices/devices/android/emulator-5554
mcp://test-devices/devices/ios/00008120-001C25D40C0A002E
mcp://test-devices/devices/windows/DESKTOP-ABC123
```

#### 1.2 资源层次结构

```
mcp://test-devices/
├── devices/
│   ├── android/
│   │   ├── {device_id_1}/
│   │   │   ├── device.json      # 设备信息文件
│   │   │   ├── logs/            # 设备日志目录
│   │   │   └── files/           # 设备文件目录
│   │   └── {device_id_2}/
│   ├── ios/
│   │   ├── {device_id_1}/
│   │   │   ├── device.json      # 设备信息文件
│   │   │   ├── logs/            # 设备日志目录
│   │   │   └── files/           # 设备文件目录
│   │   └── {device_id_2}/
│   └── windows/
│       ├── {device_id_1}/
│       │   ├── device.json      # 设备信息文件
│       │   ├── logs/            # 设备日志目录
│       │   └── files/           # 设备文件目录
│       └── {device_id_2}/
├── tools/
└── status/
```

#### 1.3 设备JSON文件结构

每个设备文件夹下的 `device.json` 文件包含以下信息：

```json
{
  "device_id": "emulator-5554",
  "name": "Android测试设备",
  "type": "android",
  "sku": "ANDROID-TEST-001",
  "cpu_type": "x86_64",
  "specs": {
    "model": "Android SDK built for x86",
    "android_version": "11",
    "manufacturer": "Google",
    "memory": "4GB",
    "storage": "32GB"
  },
  "status": "available",
  "current_borrower": null,
  "borrow_history": [
    {
      "borrower": "张三",
      "borrow_date": "2024-01-01T10:00:00Z",
      "return_date": "2024-01-01T18:00:00Z",
      "purpose": "功能测试"
    }
  ],
  "last_updated": "2024-01-01T12:00:00Z",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### 2. 工具调用 (Tools)

#### 2.1 设备管理工具

##### `device.list`
**描述**: 列出所有可用设备

**参数**: 无

**返回示例**:
```json
{
  "devices": [
    {
      "id": "emulator-5554",
      "type": "android",
      "name": "Android Emulator",
      "status": "connected",
      "info": {
        "model": "Android SDK built for x86",
        "android_version": "11",
        "manufacturer": "Google"
      }
    }
  ]
}
```

##### `device.connect`
**描述**: 连接指定设备

**参数**:
```json
{
  "device_id": "string"
}
```

**返回示例**:
```json
{
  "success": true,
  "device_id": "emulator-5554"
}
```

##### `device.disconnect`
**描述**: 断开指定设备连接

**参数**:
```json
{
  "device_id": "string"
}
```

**返回示例**:
```json
{
  "success": true,
  "device_id": "emulator-5554"
}
```

##### `device.execute`
**描述**: 在设备上执行命令

**参数**:
```json
{
  "device_id": "string",
  "command": "string"
}
```

**返回示例**:
```json
{
  "success": true,
  "output": "command output",
  "error": "",
  "device_id": "emulator-5554"
}
```

##### `device.upload`
**描述**: 向设备上传文件

**参数**:
```json
{
  "device_id": "string",
  "local_path": "string",
  "remote_path": "string"
}
```

**返回示例**:
```json
{
  "success": true,
  "local_path": "/path/to/file",
  "remote_path": "/sdcard/file",
  "device_id": "emulator-5554"
}
```

##### `device.download`
**描述**: 从设备下载文件

**参数**:
```json
{
  "device_id": "string",
  "remote_path": "string",
  "local_path": "string"
}
```

**返回示例**:
```json
{
  "success": true,
  "remote_path": "/sdcard/file",
  "local_path": "/path/to/file",
  "device_id": "emulator-5554"
}
```

##### `device.status`
**描述**: 获取设备状态信息

**参数**:
```json
{
  "device_id": "string"
}
```

**返回示例**:
```json
{
  "device_id": "emulator-5554",
  "name": "Android测试设备",
  "type": "android",
  "sku": "ANDROID-TEST-001",
  "cpu_type": "x86_64",
  "status": "available",
  "current_borrower": null,
  "specs": {
    "model": "Android SDK built for x86",
    "android_version": "11",
    "manufacturer": "Google",
    "memory": "4GB",
    "storage": "32GB"
  },
  "borrow_history": [
    {
      "borrower": "张三",
      "borrow_date": "2024-01-01T10:00:00Z",
      "return_date": "2024-01-01T18:00:00Z",
      "purpose": "功能测试"
    }
  ],
  "last_updated": "2024-01-01T12:00:00Z"
}
```

##### `device.borrow`
**描述**: 借用设备

**参数**:
```json
{
  "device_id": "string",
  "borrower": "string",
  "purpose": "string",
  "expected_return_date": "string"
}
```

**返回示例**:
```json
{
  "success": true,
  "device_id": "emulator-5554",
  "borrower": "张三",
  "borrow_date": "2024-01-01T12:00:00Z",
  "expected_return_date": "2024-01-02T12:00:00Z",
  "purpose": "功能测试"
}
```

##### `device.return`
**描述**: 归还设备

**参数**:
```json
{
  "device_id": "string",
  "returner": "string"
}
```

**返回示例**:
```json
{
  "success": true,
  "device_id": "emulator-5554",
  "returner": "张三",
  "return_date": "2024-01-01T18:00:00Z",
  "borrow_duration": "6h 0m"
}
```

##### `device.info`
**描述**: 获取设备详细信息

**参数**:
```json
{
  "device_id": "string"
}
```

**返回示例**:
```json
{
  "device_id": "emulator-5554",
  "name": "Android测试设备",
  "type": "android",
  "sku": "ANDROID-TEST-001",
  "cpu_type": "x86_64",
  "specs": {
    "model": "Android SDK built for x86",
    "android_version": "11",
    "manufacturer": "Google",
    "memory": "4GB",
    "storage": "32GB"
  },
  "status": "available",
  "current_borrower": null,
  "borrow_history": [
    {
      "borrower": "张三",
      "borrow_date": "2024-01-01T10:00:00Z",
      "return_date": "2024-01-01T18:00:00Z",
      "purpose": "功能测试"
    }
  ],
  "created_at": "2024-01-01T00:00:00Z",
  "last_updated": "2024-01-01T12:00:00Z"
}
```

##### `device.create`
**描述**: 创建设备记录

**参数**:
```json
{
  "device_id": "string",
  "name": "string",
  "type": "string",
  "sku": "string",
  "cpu_type": "string",
  "specs": {
    "model": "string",
    "version": "string",
    "manufacturer": "string",
    "memory": "string",
    "storage": "string"
  }
}
```

**返回示例**:
```json
{
  "success": true,
  "device_id": "emulator-5554",
  "message": "设备创建成功"
}
```

##### `device.update`
**描述**: 更新设备信息

**参数**:
```json
{
  "device_id": "string",
  "updates": {
    "name": "string",
    "specs": "object"
  }
}
```

**返回示例**:
```json
{
  "success": true,
  "device_id": "emulator-5554",
  "message": "设备信息更新成功"
}
```

##### `device.delete`
**描述**: 删除设备记录

**参数**:
```json
{
  "device_id": "string"
}
```

**返回示例**:
```json
{
  "success": true,
  "device_id": "emulator-5554",
  "message": "设备删除成功"
}
```

##### `device.search`
**描述**: 搜索设备

**参数**:
```json
{
  "query": "string",
  "filters": {
    "type": "string",
    "status": "string",
    "cpu_type": "string",
    "available": "boolean"
  }
}
```

**返回示例**:
```json
{
  "devices": [
    {
      "device_id": "emulator-5554",
      "name": "Android测试设备",
      "type": "android",
      "sku": "ANDROID-TEST-001",
      "status": "available"
    }
  ],
  "total": 1
}
```

#### 2.2 系统管理工具

##### `system.info`
**描述**: 获取系统信息

**参数**: 无

**返回示例**:
```json
{
  "system": {
    "version": "1.0.0",
    "uptime": "2h 15m 30s",
    "devices_count": 3,
    "memory_usage": "45%",
    "cpu_usage": "12%"
  }
}
```

##### `system.restart`
**描述**: 重启系统服务

**参数**: 无

**返回示例**:
```json
{
  "success": true,
  "message": "System restarting in 5 seconds"
}
```

## 🔌 HTTP REST接口

### 1. 系统接口

#### 1.1 健康检查
```http
GET /health
```

**响应**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "version": "1.0.0"
}
```

#### 1.2 API文档
```http
GET /docs          # Swagger UI
GET /redoc         # ReDoc
GET /openapi.json  # OpenAPI规范
```

### 2. 资源管理接口

#### 2.1 列出所有资源
```http
GET /resources
```

**响应**:
```json
[
  {
    "uri": "mcp://test-devices/",
    "name": "Test Device Management",
    "description": "MCP测试设备管理系统根资源",
    "mimeType": "application/json",
    "contents": {
      "type": "directory",
      "children": [
        "mcp://test-devices/devices",
        "mcp://test-devices/tools",
        "mcp://test-devices/status"
      ]
    }
  }
]
```

#### 2.2 获取特定资源
```http
GET /resources/{uri:path}
```

**参数**:
- `uri`: 资源URI路径

**响应**: 返回指定资源的内容

### 3. 工具调用接口

#### 3.1 列出所有工具
```http
GET /tools
```

**响应**:
```json
[
  {
    "name": "device.list",
    "description": "列出所有可用设备",
    "inputSchema": {
      "type": "object",
      "properties": {},
      "required": []
    }
  },
  {
    "name": "device.connect",
    "description": "连接指定设备",
    "inputSchema": {
      "type": "object",
      "properties": {
        "device_id": {"type": "string"}
      },
      "required": ["device_id"]
    }
  },
  {
    "name": "device.disconnect",
    "description": "断开指定设备连接",
    "inputSchema": {
      "type": "object",
      "properties": {
        "device_id": {"type": "string"}
      },
      "required": ["device_id"]
    }
  },
  {
    "name": "device.execute",
    "description": "在设备上执行命令",
    "inputSchema": {
      "type": "object",
      "properties": {
        "device_id": {"type": "string"},
        "command": {"type": "string"}
      },
      "required": ["device_id", "command"]
    }
  },
  {
    "name": "device.upload",
    "description": "向设备上传文件",
    "inputSchema": {
      "type": "object",
      "properties": {
        "device_id": {"type": "string"},
        "local_path": {"type": "string"},
        "remote_path": {"type": "string"}
      },
      "required": ["device_id", "local_path", "remote_path"]
    }
  },
  {
    "name": "device.download",
    "description": "从设备下载文件",
    "inputSchema": {
      "type": "object",
      "properties": {
        "device_id": {"type": "string"},
        "remote_path": {"type": "string"},
        "local_path": {"type": "string"}
      },
      "required": ["device_id", "remote_path", "local_path"]
    }
  },
  {
    "name": "device.status",
    "description": "获取设备状态信息",
    "inputSchema": {
      "type": "object",
      "properties": {
        "device_id": {"type": "string"}
      },
      "required": ["device_id"]
    }
  },
  {
    "name": "device.borrow",
    "description": "借用设备",
    "inputSchema": {
      "type": "object",
      "properties": {
        "device_id": {"type": "string"},
        "borrower": {"type": "string"},
        "purpose": {"type": "string"},
        "expected_return_date": {"type": "string"}
      },
      "required": ["device_id", "borrower", "purpose", "expected_return_date"]
    }
  },
  {
    "name": "device.return",
    "description": "归还设备",
    "inputSchema": {
      "type": "object",
      "properties": {
        "device_id": {"type": "string"},
        "returner": {"type": "string"}
      },
      "required": ["device_id", "returner"]
    }
  },
  {
    "name": "device.info",
    "description": "获取设备详细信息",
    "inputSchema": {
      "type": "object",
      "properties": {
        "device_id": {"type": "string"}
      },
      "required": ["device_id"]
    }
  },
  {
    "name": "device.create",
    "description": "创建设备记录",
    "inputSchema": {
      "type": "object",
      "properties": {
        "device_id": {"type": "string"},
        "name": {"type": "string"},
        "type": {"type": "string"},
        "sku": {"type": "string"},
        "cpu_type": {"type": "string"},
        "specs": {"type": "object"}
      },
      "required": ["device_id", "name", "type", "sku", "cpu_type"]
    }
  },
  {
    "name": "device.update",
    "description": "更新设备信息",
    "inputSchema": {
      "type": "object",
      "properties": {
        "device_id": {"type": "string"},
        "updates": {"type": "object"}
      },
      "required": ["device_id", "updates"]
    }
  },
  {
    "name": "device.delete",
    "description": "删除设备记录",
    "inputSchema": {
      "type": "object",
      "properties": {
        "device_id": {"type": "string"}
      },
      "required": ["device_id"]
    }
  },
  {
    "name": "device.search",
    "description": "搜索设备",
    "inputSchema": {
      "type": "object",
      "properties": {
        "query": {"type": "string"},
        "filters": {"type": "object"}
      },
      "required": []
    }
  }
]
```

#### 3.2 调用工具
```http
POST /tools/{name}/call
```

**参数**:
- `name`: 工具名称
- `arguments`: 工具参数 (JSON)

**请求体示例**:
```json
{
  "device_id": "emulator-5554",
  "command": "ls /sdcard"
}
```

**响应**: 返回工具执行结果

### 4. 设备管理接口

#### 4.1 列出所有设备
```http
GET /tools/device.list
```

**响应**: 同 `device.list` 工具

#### 4.2 连接设备
```http
POST /tools/device.connect
```

**请求体**:
```json
{
  "device_id": "emulator-5554"
}
```

**响应**: 同 `device.connect` 工具

#### 4.3 断开设备
```http
POST /tools/device.disconnect
```

**请求体**:
```json
{
  "device_id": "emulator-5554"
}
```

**响应**: 同 `device.disconnect` 工具

#### 4.4 执行命令
```http
POST /tools/device.execute
```

**请求体**:
```json
{
  "device_id": "emulator-5554",
  "command": "ls /sdcard"
}
```

**响应**: 同 `device.execute` 工具

#### 4.5 获取设备信息
```http
POST /tools/device.info
```

**请求体**:
```json
{
  "device_id": "emulator-5554"
}
```

**响应**: 同 `device.info` 工具

#### 4.6 借用设备
```http
POST /tools/device.borrow
```

**请求体**:
```json
{
  "device_id": "emulator-5554",
  "borrower": "张三",
  "purpose": "功能测试",
  "expected_return_date": "2024-01-02T12:00:00Z"
}
```

**响应**: 同 `device.borrow` 工具

#### 4.7 归还设备
```http
POST /tools/device.return
```

**请求体**:
```json
{
  "device_id": "emulator-5554",
  "returner": "张三"
}
```

**响应**: 同 `device.return` 工具

#### 4.8 创建设备
```http
POST /tools/device.create
```

**请求体**:
```json
{
  "device_id": "emulator-5554",
  "name": "Android测试设备",
  "type": "android",
  "sku": "ANDROID-TEST-001",
  "cpu_type": "x86_64",
  "specs": {
    "model": "Android SDK built for x86",
    "version": "11",
    "manufacturer": "Google",
    "memory": "4GB",
    "storage": "32GB"
  }
}
```

**响应**: 同 `device.create` 工具

#### 4.9 更新设备
```http
POST /tools/device.update
```

**请求体**:
```json
{
  "device_id": "emulator-5554",
  "updates": {
    "name": "Android测试设备V2",
    "specs": {
      "memory": "8GB"
    }
  }
}
```

**响应**: 同 `device.update` 工具

#### 4.10 删除设备
```http
POST /tools/device.delete
```

**请求体**:
```json
{
  "device_id": "emulator-5554"
}
```

**响应**: 同 `device.delete` 工具

#### 4.11 搜索设备
```http
POST /tools/device.search
```

**请求体**:
```json
{
  "query": "Android",
  "filters": {
    "type": "android",
    "status": "available",
    "available": true
  }
}
```

**响应**: 同 `device.search` 工具

## 📡 WebSocket接口

### 连接地址
```
ws://localhost:8000/ws
```

### 消息格式

#### 设备状态更新
```json
{
  "type": "device_status_update",
  "data": {
    "device_id": "emulator-5554",
    "status": "connected",
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

#### 系统事件
```json
{
  "type": "system_event",
  "data": {
    "event": "device_discovered",
    "device_id": "emulator-5554",
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

#### 设备借用事件
```json
{
  "type": "device_borrowed",
  "data": {
    "device_id": "emulator-5554",
    "borrower": "张三",
    "purpose": "功能测试",
    "borrow_date": "2024-01-01T12:00:00Z",
    "expected_return_date": "2024-01-02T12:00:00Z",
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

#### 设备归还事件
```json
{
  "type": "device_returned",
  "data": {
    "device_id": "emulator-5554",
    "returner": "张三",
    "return_date": "2024-01-01T18:00:00Z",
    "borrow_duration": "6h 0m",
    "timestamp": "2024-01-01T18:00:00Z"
  }
}
```

#### 错误通知
```json
{
  "type": "error",
  "data": {
    "code": "DEVICE_CONNECTION_FAILED",
    "message": "设备连接失败",
    "device_id": "emulator-5554",
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

## 📊 监控接口

### 系统指标
```http
GET /metrics
```

**端口**: 9090

**响应**: Prometheus格式的指标数据

## 🔧 错误处理

### 错误响应格式
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述",
    "details": "详细错误信息",
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

### 常见错误代码

| 错误代码 | 描述 | HTTP状态码 |
|---------|------|-----------|
| `DEVICE_NOT_FOUND` | 设备未找到 | 404 |
| `DEVICE_CONNECTION_FAILED` | 设备连接失败 | 500 |
| `COMMAND_EXECUTION_FAILED` | 命令执行失败 | 500 |
| `INVALID_PARAMETERS` | 参数无效 | 400 |
| `INTERNAL_ERROR` | 内部错误 | 500 |

## 📝 使用示例

### 1. 使用curl管理设备

```bash
# 列出所有设备
curl http://localhost:8000/tools/device.list

# 连接Android设备
curl -X POST http://localhost:8000/tools/device.connect \
  -H "Content-Type: application/json" \
  -d '{"device_id": "emulator-5554"}'

# 执行命令
curl -X POST http://localhost:8000/tools/device.execute \
  -H "Content-Type: application/json" \
  -d '{"device_id": "emulator-5554", "command": "ls /sdcard"}'

# 获取设备状态
curl -X POST http://localhost:8000/tools/device.status \
  -H "Content-Type: application/json" \
  -d '{"device_id": "emulator-5554"}'

# 借用设备
curl -X POST http://localhost:8000/tools/device.borrow \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "emulator-5554",
    "borrower": "张三",
    "purpose": "功能测试",
    "expected_return_date": "2024-01-02T12:00:00Z"
  }'

# 归还设备
curl -X POST http://localhost:8000/tools/device.return \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "emulator-5554",
    "returner": "张三"
  }'

# 创建设备
curl -X POST http://localhost:8000/tools/device.create \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "emulator-5554",
    "name": "Android测试设备",
    "type": "android",
    "sku": "ANDROID-TEST-001",
    "cpu_type": "x86_64",
    "specs": {
      "model": "Android SDK built for x86",
      "version": "11",
      "manufacturer": "Google",
      "memory": "4GB",
      "storage": "32GB"
    }
  }'

# 搜索设备
curl -X POST http://localhost:8000/tools/device.search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Android",
    "filters": {
      "type": "android",
      "status": "available",
      "available": true
    }
  }'
```

### 2. 使用Python客户端

```python
import requests
import json
from datetime import datetime, timedelta

base_url = "http://localhost:8000"

# 列出所有设备
response = requests.get(f"{base_url}/tools/device.list")
devices = response.json()
print(f"发现 {len(devices['devices'])} 个设备")

# 连接设备
device_id = "emulator-5554"
response = requests.post(
    f"{base_url}/tools/device.connect",
    json={"device_id": device_id}
)
print(f"设备连接: {response.json()}")

# 执行命令
response = requests.post(
    f"{base_url}/tools/device.execute",
    json={"device_id": device_id, "command": "ls /sdcard"}
)
result = response.json()
print(f"命令执行结果: {result}")

# 借用设备
expected_return = (datetime.now() + timedelta(days=1)).isoformat()
borrow_data = {
    "device_id": device_id,
    "borrower": "张三",
    "purpose": "功能测试",
    "expected_return_date": expected_return
}
response = requests.post(
    f"{base_url}/tools/device.borrow",
    json=borrow_data
)
print(f"设备借用: {response.json()}")

# 获取设备信息
response = requests.post(
    f"{base_url}/tools/device.info",
    json={"device_id": device_id}
)
device_info = response.json()
print(f"设备信息: {device_info}")

# 归还设备
response = requests.post(
    f"{base_url}/tools/device.return",
    json={"device_id": device_id, "returner": "张三"}
)
print(f"设备归还: {response.json()}")

# 搜索可用设备
search_data = {
    "query": "Android",
    "filters": {
        "type": "android",
        "status": "available",
        "available": True
    }
}
response = requests.post(
    f"{base_url}/tools/device.search",
    json=search_data
)
search_results = response.json()
print(f"搜索结果: {search_results}")
```

### 3. 使用WebSocket监听状态

```python
import websockets
import asyncio
import json

async def listen_device_status():
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as websocket:
        print("已连接到WebSocket服务器")
        
        while True:
            try:
                message = await websocket.recv()
                data = json.loads(message)
                
                if data["type"] == "device_status_update":
                    device_id = data["data"]["device_id"]
                    status = data["data"]["status"]
                    print(f"设备 {device_id} 状态更新: {status}")
                    
                elif data["type"] == "device_borrowed":
                    device_id = data["data"]["device_id"]
                    borrower = data["data"]["borrower"]
                    purpose = data["data"]["purpose"]
                    print(f"设备 {device_id} 被 {borrower} 借用，用途: {purpose}")
                    
                elif data["type"] == "device_returned":
                    device_id = data["data"]["device_id"]
                    returner = data["data"]["returner"]
                    duration = data["data"]["borrow_duration"]
                    print(f"设备 {device_id} 被 {returner} 归还，借用时长: {duration}")
                    
                elif data["type"] == "system_event":
                    event = data["data"]["event"]
                    device_id = data["data"]["device_id"]
                    print(f"系统事件: {event} - 设备: {device_id}")
                    
            except websockets.exceptions.ConnectionClosed:
                print("WebSocket连接已关闭")
                break

# 运行WebSocket客户端
asyncio.run(listen_device_status())
```

## 📋 接口限制

### 请求限制
- **速率限制**: 100 请求/分钟
- **超时时间**: 30秒
- **最大文件大小**: 100MB

### 支持的文件类型
- `.apk` - Android应用包
- `.ipa` - iOS应用包
- `.exe` - Windows可执行文件
- `.zip` - 压缩文件
- `.txt` - 文本文件
- `.log` - 日志文件

## 🔄 版本信息

- **当前版本**: 1.0.0
- **MCP协议版本**: 1.0
- **最后更新**: 2024-01-01

## 📞 支持

如有问题或建议，请：
1. 查看 [常见问题](../QUICKSTART.md#-常见问题)
2. 搜索 [Issues](../../issues)
3. 创建新的 Issue

## 📁 相关文件

- [设备JSON模板](device_template.json) - 设备信息文件的完整模板
- [快速开始指南](../QUICKSTART.md) - 项目设置和使用说明
- [开发指导](../DEVELOPMENT_GUIDE.md) - 详细的开发文档

---

**注意**: 这是一个开发中的项目，API可能会发生变化。请查看最新文档获取最新信息。
