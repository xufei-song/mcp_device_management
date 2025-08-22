                                  

## 项目概述

这是一个基于MCP（Model Context Protocol）的测试设备管理系统，用于管理和监控不同类型的测试设备，包括Android、iOS和Windows设备。

## 项目结构

```
TestDeviceManagmentMCP/
├── Devices/                    # 设备目录
│   ├── Android/               # Android设备
│   ├── IOS/                   # iOS设备
│   └── Windows/               # Windows设备
├── src/                       # 源代码目录
│   ├── mcp/                   # MCP协议实现
│   ├── device/                # 设备管理核心
│   ├── handlers/              # 请求处理器
│   └── utils/                 # 工具函数
├── config/                    # 配置文件
├── tests/                     # 测试文件
├── docs/                      # 文档
└── requirements.txt           # 依赖包
```

## 核心功能设计

### 1. 设备管理
- **设备注册**: 自动发现和注册新设备
- **设备分类**: 按类型（Android/iOS/Windows）组织设备
- **设备状态**: 实时监控设备状态（在线/离线/忙碌/空闲）
- **设备信息**: 存储设备详细信息（型号、版本、能力等）

### 2. MCP协议实现
- **资源管理**: 实现MCP资源管理接口
- **工具调用**: 提供设备操作工具
- **事件通知**: 设备状态变化事件推送

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
- **通信**: WebSocket (实时状态更新)
- **序列化**: JSON/YAML (配置文件)

### MCP协议实现
```python
# 示例MCP服务器结构
class TestDeviceMCPServer:
    def __init__(self):
        self.device_manager = DeviceManager()
        self.resource_manager = ResourceManager()
    
    async def list_resources(self) -> List[Resource]:
        # 返回所有设备资源
        pass
    
    async def read_resource(self, uri: str) -> Resource:
        # 读取特定设备信息
        pass
    
    async def list_tools(self) -> List[Tool]:
        # 返回可用工具列表
        pass
    
    async def call_tool(self, name: str, arguments: Dict) -> ToolResult:
        # 执行工具调用
        pass
```

## 开发阶段规划

### 第一阶段：基础架构
1. **项目初始化**
   - 创建Python项目结构
   - 安装必要依赖
   - 配置开发环境

2. **MCP协议框架**
   - 实现基础MCP服务器
   - 定义资源结构
   - 实现工具接口

3. **设备管理器**
   - 创建设备基类
   - 实现设备发现机制
   - 建立设备状态管理

### 第二阶段：设备集成
1. **Android设备支持**
   - ADB连接管理
   - 设备信息获取
   - 命令执行接口

2. **iOS设备支持**
   - libimobiledevice集成
   - 设备配对管理
   - 应用安装/卸载

3. **Windows设备支持**
   - WMI/WinRM连接
   - 系统信息收集
   - 远程命令执行

### 第三阶段：高级功能
1. **实时监控**
   - WebSocket状态推送
   - 设备健康检查
   - 告警机制

2. **测试自动化**
   - 测试脚本执行
   - 结果收集分析
   - 报告生成

3. **用户界面**
   - Web管理界面
   - 设备状态展示
   - 操作控制面板

## 关键接口设计

### 设备资源URI格式
```
mcp://test-devices/devices/{device_type}/{device_id}
mcp://test-devices/devices/android/emulator-5554
mcp://test-devices/devices/ios/00008120-001C25D40C0A002E
mcp://test-devices/devices/windows/DESKTOP-ABC123
```

### 核心工具列表
1. **device.list** - 列出所有设备
2. **device.connect** - 连接设备
3. **device.disconnect** - 断开设备
4. **device.execute** - 执行命令
5. **device.upload** - 上传文件
6. **device.download** - 下载文件
7. **device.status** - 获取设备状态

## 配置文件示例

### MCP服务器配置
```yaml
# config/mcp_server.yaml
server:
  host: "localhost"
  port: 8000
  debug: true

devices:
  android:
    adb_path: "/usr/local/bin/adb"
    auto_discover: true
  ios:
    libimobiledevice_path: "/usr/local/bin/ideviceinfo"
    pairing_timeout: 30
  windows:
    winrm_port: 5985

logging:
  level: "INFO"
  file: "logs/mcp_server.log"
```

## 开发环境设置

### 1. 安装依赖
```bash
pip install fastapi uvicorn pydantic sqlalchemy websockets
pip install pyyaml python-dotenv
```

### 2. 环境变量
```bash
# .env
MCP_SERVER_HOST=localhost
MCP_SERVER_PORT=8000
DEVICE_DISCOVERY_INTERVAL=30
LOG_LEVEL=INFO
```

### 3. 开发工具
- **代码编辑器**: VS Code + Python扩展
- **调试工具**: Python debugger (pdb)
- **API测试**: Postman/Insomnia
- **数据库**: SQLite Browser

## 测试策略

### 单元测试
- MCP协议实现测试
- 设备管理器测试
- 工具函数测试

### 集成测试
- 设备连接测试
- 命令执行测试
- 状态同步测试

### 端到端测试
- 完整工作流程测试
- 多设备并发测试
- 错误处理测试

## 部署说明

### 开发环境
```cmd
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 生产环境
```cmd
# 使用gunicorn (需要先安装)
pip install gunicorn
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 贡献指南

1. **代码规范**: 遵循PEP 8 Python代码规范
2. **文档**: 所有新功能需要更新文档
3. **测试**: 新功能需要包含相应的测试用例
4. **提交**: 使用清晰的提交信息

## 下一步行动

1. 创建项目基础结构
2. 实现MCP协议框架
3. 开发设备管理器
4. 集成Android设备支持
5. 添加iOS和Windows设备支持
6. 实现实时监控功能
7. 开发Web管理界面

## 联系方式

如有问题或建议，请通过以下方式联系：
- 项目仓库: [GitHub Repository]
- 问题反馈: [Issues]
- 讨论区: [Discussions]

---

**注意**: 这是一个开发指导文档，在实际开发过程中可能需要根据具体需求和环境进行调整。


# 1. 运行设置脚本（只需要运行一次）
scripts\setup.bat

# 2. 激活虚拟环境
venv\Scripts\activate.bat

# 3. 启动MCP服务器
python run_mcp_server.py