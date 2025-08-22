# MCP测试设备管理系统 - 快速开始指南

## 🚀 快速开始

### 1. 环境要求

- Python 3.8 或更高版本
- Git
- ADB (用于Android设备管理)
- libimobiledevice (用于iOS设备管理，可选)

### 2. 克隆项目

```bash
git clone <your-repository-url>
cd TestDeviceManagmentMCP
```

### 3. 自动设置 (推荐)

```cmd
scripts\setup.bat
```

### 4. 手动设置

如果自动设置失败，可以手动执行以下步骤：

```cmd
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate

# 安装依赖
pip install -e .
pip install -e ".[dev]"

# 创建必要目录
mkdir src\mcp src\device src\handlers src\utils
mkdir config tests docs logs data
```

### 5. 配置环境

```bash
# 复制环境变量文件
cp .env.example .env

# 编辑配置文件
# 根据需要修改 config/settings.yaml
```

### 6. 启动开发服务器

```cmd
scripts\run_dev.bat
```

服务器将在 http://localhost:8000 启动

## 📱 设备管理

### Android设备

1. **安装ADB**
   ```bash
   # Ubuntu/Debian
   sudo apt install android-tools-adb
   
   # macOS
   brew install android-platform-tools
   
   # Windows
   # 下载Android SDK Platform Tools
   ```

2. **连接设备**
   ```bash
   adb devices
   ```

3. **通过MCP管理**
   ```bash
   # 列出设备
   curl http://localhost:8000/tools/device.list
   
   # 连接设备
   curl -X POST http://localhost:8000/tools/device.connect \
     -H "Content-Type: application/json" \
     -d '{"device_id": "your-device-id"}'
   ```

### iOS设备

1. **安装libimobiledevice**
   ```bash
   # Ubuntu/Debian
   sudo apt install libimobiledevice6 libimobiledevice-utils
   
   # macOS
   brew install libimobiledevice
   ```

2. **连接设备**
   ```bash
   idevice_id -l
   ```

### Windows设备

1. **配置WinRM**
   ```powershell
   # 在Windows设备上启用WinRM
   Enable-PSRemoting -Force
   ```

## 🔧 开发工具

### 代码格式化
```cmd
scripts\format.bat
```

### 运行测试
```cmd
scripts\run_tests.bat
```

### 代码检查
```cmd
# 类型检查
mypy src\

# 代码风格检查
flake8 src\

# 安全检查
bandit src\
```

## 📚 API文档

启动服务器后，访问以下地址查看API文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🔍 调试

### 查看日志
```bash
tail -f logs/mcp_server.log
```

### 启用调试模式
```cmd
set LOG_LEVEL=DEBUG
scripts\run_dev.bat
```

### 使用调试器
```python
import pdb; pdb.set_trace()
```

## 🚨 常见问题

### 1. 端口被占用
```cmd
# 查找占用端口的进程
netstat -ano | findstr :8000

# 杀死进程
taskkill /PID <PID> /F
```

### 2. 权限问题
```cmd
# Windows下脚本通常不需要特殊权限设置
# 如果遇到问题，请以管理员身份运行命令提示符
```

### 3. 依赖安装失败
```cmd
# 升级pip
python -m pip install --upgrade pip

# 清理缓存
pip cache purge

# 重新安装
pip install -e . --force-reinstall
```

### 4. 设备连接失败
- 检查设备是否已连接
- 确认ADB服务是否运行
- 检查设备USB调试是否启用

## 📖 更多文档

- [开发指导](DEVELOPMENT_GUIDE.md) - 详细的开发文档
- [MCP API接口](docs/MCP_API.md) - 完整的MCP协议和HTTP API文档
- [部署指南](docs/deployment.md) - 生产环境部署

## 🤝 贡献

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🆘 支持

如果遇到问题，请：

1. 查看 [常见问题](#-常见问题) 部分
2. 搜索 [Issues](../../issues)
3. 创建新的 Issue

---

**注意**: 这是一个开发中的项目，API可能会发生变化。请查看最新文档获取最新信息。
