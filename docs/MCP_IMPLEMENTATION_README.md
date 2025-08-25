# MCP测试设备管理系统 - 实现说明

## 🎯 项目概述

本项目实现了基于MCP（Model Context Protocol）协议的测试设备管理系统，支持Android、iOS和Windows设备的统一管理，包括设备信息维护、借用管理、状态监控等核心功能。

## 🏗️ 系统架构

### 核心组件

1. **设备管理器 (DeviceManager)**
   - 负责设备的CRUD操作
   - 管理设备借用和归还流程
   - 支持设备搜索和过滤

2. **MCP协议实现 (MCPProtocol)**
   - 实现MCP协议规范
   - 提供工具调用接口
   - 支持14个核心设备管理工具

3. **HTTP API处理器 (API Handlers)**
   - 提供RESTful API接口
   - 支持所有MCP工具功能
   - 完整的错误处理和响应

4. **数据模型 (Models)**
   - 基于Pydantic的数据验证
   - 完整的设备信息结构
   - 借用历史和维护记录

## 📁 项目结构

```
TestDeviceManagmentMCP/
├── src/                           # 源代码目录
│   ├── device/                    # 设备管理模块
│   │   ├── models.py             # 数据模型定义
│   │   └── manager.py            # 设备管理器
│   ├── mcp/                      # MCP协议实现
│   │   └── protocol.py           # MCP协议核心
│   ├── handlers/                 # 请求处理器
│   │   └── api.py                # HTTP API处理器
│   ├── utils/                    # 工具函数
│   └── main.py                   # 主应用入口
├── Devices/                       # 设备数据目录
│   ├── Android/                  # Android设备
│   ├── IOS/                      # iOS设备
│   └── Windows/                  # Windows设备
├── tests/                        # 测试文件
├── docs/                         # 文档目录
└── run_mcp_server.py             # 启动脚本
```

## 🚀 快速开始

### 1. 安装依赖

```bash
# 安装项目依赖
pip install -e .

# 安装开发依赖
pip install -e ".[dev]"
```

### 2. 启动服务器

```bash
# 使用启动脚本
python run_mcp_server.py

# 或直接使用uvicorn
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. 访问系统

- **主页面**: http://localhost:8000/
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

## 🔧 核心功能

### 设备管理工具

| 工具名称 | 功能描述 | HTTP接口 |
|---------|---------|----------|
| `device.list` | 列出所有设备 | `GET /api/tools/device.list` |
| `device.create` | 创建设备记录 | `POST /api/tools/device.create` |
| `device.info` | 获取设备详情 | `POST /api/tools/device.info` |
| `device.update` | 更新设备信息 | `POST /api/tools/device.update` |
| `device.delete` | 删除设备记录 | `POST /api/tools/device.delete` |
| `device.search` | 搜索设备 | `POST /api/tools/device.search` |

### 设备操作工具

| 工具名称 | 功能描述 | HTTP接口 |
|---------|---------|----------|
| `device.connect` | 连接设备 | `POST /api/tools/device.connect` |
| `device.disconnect` | 断开设备 | `POST /api/tools/device.disconnect` |
| `device.execute` | 执行命令 | `POST /api/tools/device.execute` |
| `device.upload` | 上传文件 | `POST /api/tools/device.upload` |
| `device.download` | 下载文件 | `POST /api/tools/device.download` |
| `device.status` | 获取状态 | `POST /api/tools/device.status` |

### 借用管理工具

| 工具名称 | 功能描述 | HTTP接口 |
|---------|---------|----------|
| `device.borrow` | 借用设备 | `POST /api/tools/device.borrow` |
| `device.return` | 归还设备 | `POST /api/tools/device.return` |

## 📊 数据模型

### 设备信息结构

```json
{
  "device_id": "设备唯一标识",
  "name": "设备显示名称",
  "type": "设备类型 (android|ios|windows)",
  "sku": "设备SKU编号",
  "cpu_type": "CPU类型",
  "specs": {
    "model": "设备型号",
    "version": "系统版本",
    "manufacturer": "制造商",
    "memory": "内存大小",
    "storage": "存储大小"
  },
  "status": "设备状态",
  "current_borrower": "当前借用者",
  "borrow_history": "借用历史记录",
  "maintenance_history": "维护历史记录"
}
```

## 🔌 API使用示例

### 1. 列出所有设备

```bash
curl http://localhost:8000/api/tools/device.list
```

### 2. 创建设备

```bash
curl -X POST http://localhost:8000/api/tools/device.create \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "test-device-001",
    "name": "测试设备",
    "type": "android",
    "sku": "TEST-001",
    "cpu_type": "x86_64",
    "specs": {
      "model": "Test Model",
      "version": "1.0",
      "manufacturer": "Test Manufacturer",
      "memory": "4GB",
      "storage": "32GB"
    }
  }'
```

### 3. 借用设备

```bash
curl -X POST http://localhost:8000/api/tools/device.borrow \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "test-device-001",
    "borrower": "张三",
    "purpose": "功能测试",
    "expected_return_date": "2024-01-02T12:00:00Z"
  }'
```

### 4. 搜索设备

```bash
curl -X POST http://localhost:8000/api/tools/device.search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Android",
    "filters": {
      "type": "android",
      "status": "available"
    }
  }'
```

## 🧪 测试

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_device_manager.py

# 运行测试并显示覆盖率
pytest --cov=src
```

### 测试覆盖

测试覆盖了以下核心功能：
- 设备CRUD操作
- 设备借用和归还
- 设备搜索和过滤
- 错误处理和边界情况

## 🔧 配置

### 环境变量

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `HOST` | `0.0.0.0` | 服务器监听地址 |
| `PORT` | `8000` | 服务器端口 |
| `DEBUG` | `false` | 调试模式 |

### 设备目录配置

系统默认使用项目根目录下的 `Devices/` 文件夹作为设备数据存储目录。可以通过修改 `DeviceManager` 的初始化参数来自定义路径。

## 🚨 注意事项

1. **文件权限**: 确保系统对 `Devices/` 目录有读写权限
2. **数据备份**: 定期备份设备数据文件
3. **并发安全**: 当前实现为单线程，生产环境需要添加并发控制
4. **错误处理**: 所有API都包含完整的错误处理和响应

## 🔮 扩展功能

### 待实现功能

1. **WebSocket支持**: 实时设备状态推送
2. **设备连接管理**: 实际的设备连接和通信
3. **文件传输**: 完整的文件上传下载功能
4. **权限管理**: 用户认证和授权
5. **监控告警**: 设备状态监控和告警

### 扩展点

- 在 `DeviceManager` 中添加新的设备操作方法
- 在 `MCPProtocol` 中注册新的工具
- 在 `API Handlers` 中添加新的HTTP接口
- 扩展数据模型以支持更多设备属性

## 📞 支持

如有问题或建议，请：
1. 查看 [API文档](docs/MCP_API.md)
2. 运行测试验证功能
3. 检查日志输出
4. 提交Issue或Pull Request

---

**注意**: 这是一个开发中的项目，功能会持续完善。请查看最新文档获取最新信息。
