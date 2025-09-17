# Azure CLI & DevOps 集成模块

## 概述
本模块提供Azure CLI工具集成和Azure DevOps API调用功能，支持设备管理系统与Azure DevOps的集成。

## 核心接口

### record_in_deliverable(comment_text)

**功能描述**: 在Azure DevOps deliverable中记录评论

**参数**:
- `comment_text` (str): 要添加到deliverable discussion中的评论内容

**返回值**:
- `bool`: 成功返回True，失败返回False

**工作流程**:
1. 检测Azure CLI可用性
2. 执行Azure CLI登录
3. 获取Azure访问token
4. 创建Azure DevOps客户端
5. 向指定deliverable添加评论
6. 自动执行Azure CLI登出

**使用示例**:
```python
from record_in_deliverable import record_in_deliverable

# 记录设备借用
success = record_in_deliverable("borrow 12345678")

# 记录设备归还  
success = record_in_deliverable("return 87654321")

# 记录自定义操作
success = record_in_deliverable("maintenance completed for device XYZ")
```

**特性**:
- ✅ **无状态**: 每次调用都是独立的，不保留连接状态
- ✅ **自动清理**: 函数退出时自动执行Azure CLI登出
- ✅ **完整错误处理**: 涵盖网络、认证、API调用等各种异常情况
- ✅ **安全**: Token仅在执行期间存在，执行完毕后立即清理

**配置要求**:
- Azure CLI已安装并可访问
- 有效的Azure账户
- Azure DevOps访问权限
- 目标deliverable ID: 59278704 (固定配置)

## MCP服务器集成

本接口已集成到MCP设备管理服务器中：

### 设备借用流程
```
用户调用 borrow_device → record_in_deliverable("borrow {asset_number}") → 执行设备借用操作
```

### 设备归还流程  
```
用户调用 return_device → record_in_deliverable("return {asset_number}") → 执行设备归还操作
```

**集成特性**:
- 前置验证：Azure DevOps记录成功后才执行设备操作
- 失败隔离：Azure DevOps失败不会影响其他功能
- 操作日志：所有设备操作都会在Azure DevOps中留下记录

## 错误处理

**常见错误类型**:
1. **Azure CLI不可用**: 
   - 错误码: `[ERROR] Azure CLI not found!`
   - 解决方案: 安装Azure CLI

2. **登录失败**:
   - 错误码: `[ERROR] Azure login failed!`
   - 解决方案: 检查网络连接和账户权限

3. **Token获取失败**:
   - 错误码: `[ERROR] Failed to get Azure token!`
   - 解决方案: 重新登录或检查权限

4. **API调用失败**:
   - 错误码: `[ERROR] Failed to record comment`
   - 解决方案: 检查deliverable权限和网络连接

## 依赖包

**Python依赖**:
```bash
pip install azure-devops msrest
```

**系统依赖**:
- Azure CLI 2.0+
- 网络连接至Azure服务

## 测试

**独立测试**:
```bash
python src/az_info/record_in_deliverable.py
```

**导入测试**:
```bash
python -c "from src.az_info.record_in_deliverable import record_in_deliverable; print('Import successful')"
```

## 安全注意事项

1. **Token安全**: 访问token仅在函数执行期间存储，不会持久化
2. **会话管理**: 每次调用后自动登出，避免会话泄露
3. **权限控制**: 依赖Azure CLI的内置权限验证机制
4. **网络安全**: 所有通信通过HTTPS加密

## 性能考虑

- **延迟**: 每次调用需要完整的Azure认证流程，预计耗时2-5秒
- **频率限制**: 建议控制调用频率，避免触发Azure API限制
- **网络依赖**: 需要稳定的网络连接至Azure服务

---

## Azure CLI文档

### 官方文档链接
- **主页**: https://docs.microsoft.com/en-us/cli/azure/
- **安装指南**: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli-windows
- **命令参考**: https://docs.microsoft.com/en-us/cli/azure/reference-index

### Azure REST API文档
- **主页**: https://docs.microsoft.com/en-us/rest/api/azure/
- **认证指南**: 包含OAuth2、Azure AD等认证方法
- **API组件说明**: 请求/响应结构详解

### Azure DevOps REST API文档
- **主页**: https://docs.microsoft.com/en-us/rest/api/azure/devops/
- **认证方式**: 支持PAT、OAuth、MSAL等
- **API版本映射**: 包含TFS版本对应关系