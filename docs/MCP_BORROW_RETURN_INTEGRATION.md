# MCP服务器借用归还功能集成说明

## 📋 功能概述

已成功将设备借用/归还管理功能集成到MCP服务器 (`src/mcp_server2/server.py`) 中，新增了5个强大的MCP工具，为设备管理提供完整的API支持。

## 🔧 新增MCP工具列表

### 1. `find_device_by_asset` - 设备查找工具
**功能**: 根据资产编号查找设备信息
**参数**:
- `asset_number` (必需): 设备资产编号

**使用示例**:
```json
{
  "name": "find_device_by_asset",
  "arguments": {
    "asset_number": "18294886"
  }
}
```

**返回信息**:
- 设备基本信息（名称、类型、状态、OS、品牌）
- 借用状态（当前借用者、所属manager）
- 设备详细信息（序列号、创建日期等）
- 特殊字段（Windows的芯片架构、Android的设备类型）

### 2. `borrow_device` - 完整设备借用工具
**功能**: 执行完整的设备借用流程（添加记录 + 更新设备状态）
**参数**:
- `asset_number` (必需): 设备资产编号
- `borrower` (必需): 借用者姓名
- `reason` (可选): 借用原因

**使用示例**:
```json
{
  "name": "borrow_device", 
  "arguments": {
    "asset_number": "18294886",
    "borrower": "xufeisong",
    "reason": "开发测试"
  }
}
```

**执行流程**:
1. 验证设备资产编号存在
2. 在 `Devices/records.csv` 中添加借用记录
3. 更新原设备CSV文件中的状态为"正在使用"
4. 更新设备的借用者信息
5. 返回详细的操作结果

### 3. `return_device` - 完整设备归还工具
**功能**: 执行完整的设备归还流程（添加记录 + 更新设备状态）
**参数**:
- `asset_number` (必需): 设备资产编号
- `borrower` (必需): 归还者姓名
- `reason` (可选): 归还原因

**使用示例**:
```json
{
  "name": "return_device",
  "arguments": {
    "asset_number": "18294886", 
    "borrower": "xufeisong",
    "reason": "测试完成"
  }
}
```

**执行流程**:
1. 验证设备资产编号存在
2. 在 `Devices/records.csv` 中添加归还记录
3. 更新原设备CSV文件中的状态为"可用"
4. 清空设备的借用者信息
5. 返回详细的操作结果

### 4. `add_borrow_record` - 仅添加借用记录工具
**功能**: 仅在records.csv中添加借用记录（不更新设备状态）
**参数**:
- `asset_number` (必需): 设备资产编号
- `borrower` (必需): 借用者姓名
- `reason` (可选): 借用原因

**使用场景**: 当需要记录借用操作但不改变设备实际状态时使用

### 5. `add_return_record` - 仅添加归还记录工具
**功能**: 仅在records.csv中添加归还记录（不更新设备状态）
**参数**:
- `asset_number` (必需): 设备资产编号
- `borrower` (必需): 归还者姓名  
- `reason` (可选): 归还原因

**使用场景**: 当需要记录归还操作但不改变设备实际状态时使用

## 🔄 实时通知功能

所有工具都集成了MCP SDK的实时通知功能：
- ✅ 操作开始时发送进度通知
- ✅ 操作成功时发送确认通知
- ✅ 包含详细的日志信息（设备ID、操作者、时间戳）
- ✅ 支持断点续传和会话管理

## 📊 数据操作流程

### 借用设备完整流程:
```
用户输入 → 验证参数 → 查找设备 → 添加借用记录 → 更新设备状态 → 返回结果
```

### 归还设备完整流程:
```  
用户输入 → 验证参数 → 查找设备 → 添加归还记录 → 更新设备状态 → 返回结果
```

### 数据文件操作:
- **读取**: 从 `Devices/{android|ios|windows|other}_devices.csv` 查找设备
- **记录**: 写入 `Devices/records.csv` 添加借用/归还记录
- **更新**: 修改原设备CSV文件的状态和借用者字段

## 🛡️ 错误处理

### 参数验证:
- 检查必需参数是否提供
- 验证资产编号格式
- 确保借用者信息非空

### 业务逻辑验证:
- 验证设备是否存在
- 检查设备当前状态
- 确保文件读写权限

### 友好的错误提示:
- 详细的错误原因说明
- 建议的解决方案
- 相关工具的使用提示

## 🔧 技术实现

### MCP SDK集成:
- 使用官方MCP Python SDK标准接口
- 支持HTTP Stream传输协议
- 完整的JSON-RPC 2.0消息格式

### 代码结构:
```python
# 工具处理函数
async def _handle_borrow_device(arguments, ctx) -> list[types.ContentBlock]
async def _handle_return_device(arguments, ctx) -> list[types.ContentBlock]
async def _handle_find_device_by_asset(arguments, ctx) -> list[types.ContentBlock]
async def _handle_add_borrow_record(arguments, ctx) -> list[types.ContentBlock] 
async def _handle_add_return_record(arguments, ctx) -> list[types.ContentBlock]

# 工具注册
@app.call_tool()
@app.list_tools()
```

### 依赖关系:
- 导入 `src.device.records_reader` 中的核心API
- 复用现有的设备读取器模块
- 集成到现有的MCP服务器架构

## 📈 测试验证

### 集成测试结果:
- ✅ 设备查找功能测试通过
- ✅ 添加借用记录测试通过
- ✅ 添加归还记录测试通过
- ✅ MCP输出格式测试通过

### 测试覆盖:
- API功能正确性
- 数据文件操作
- 错误处理机制
- 输出格式规范

## 🎯 使用建议

### 推荐工作流程:
1. 使用 `find_device_by_asset` 查找设备信息
2. 使用 `borrow_device` 执行完整借用流程
3. 使用 `return_device` 执行完整归还流程
4. 使用 `get_device_records` 查看操作记录

### 最佳实践:
- 借用前先查询设备状态
- 提供清晰的借用/归还原因
- 定期检查设备记录
- 使用实时通知监控操作状态

## 🔮 扩展性

### 未来增强:
- 支持批量设备操作
- 添加设备预约功能
- 集成邮件通知系统
- 支持设备使用统计报告

### 兼容性:
- 完全兼容现有设备数据格式
- 保持向后兼容性
- 支持多种设备类型扩展

---

**最后更新**: 2025年9月17日  
**版本**: v1.0 (MCP服务器借用归还功能集成版本)  
**作者**: GitHub Copilot  
**状态**: ✅ 已完成并测试通过