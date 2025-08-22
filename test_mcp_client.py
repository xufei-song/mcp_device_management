#!/usr/bin/env python3
"""
MCP客户端测试脚本
用于测试MCP服务器是否正常工作
"""

import asyncio
import websockets
import json
from datetime import datetime


async def test_mcp_server():
    """测试MCP服务器"""
    uri = "ws://localhost:8000/mcp"
    
    try:
        print(f"[TEST] 连接到MCP服务器: {uri}")
        async with websockets.connect(uri) as websocket:
            print("[TEST] 连接成功！")
            
            # 测试1: 初始化
            print("\n[TEST] 测试1: 初始化")
            init_message = {
                "id": "init_1",
                "type": "initialize"
            }
            await websocket.send(json.dumps(init_message))
            response = await websocket.recv()
            print(f"[TEST] 初始化响应: {response}")
            
            # 测试2: 获取工具列表
            print("\n[TEST] 测试2: 获取工具列表")
            tools_message = {
                "id": "tools_1",
                "type": "tools/list"
            }
            await websocket.send(json.dumps(tools_message))
            response = await websocket.recv()
            print(f"[TEST] 工具列表响应: {response}")
            
            # 测试3: 调用工具
            print("\n[TEST] 测试3: 调用device.list工具")
            call_message = {
                "id": "call_1",
                "type": "tools/call",
                "name": "device.list",
                "arguments": {}
            }
            await websocket.send(json.dumps(call_message))
            response = await websocket.recv()
            print(f"[TEST] 工具调用响应: {response}")
            
            # 测试4: 获取资源列表
            print("\n[TEST] 测试4: 获取资源列表")
            resources_message = {
                "id": "resources_1",
                "type": "resources/list",
                "uri": "mcp://test-devices/"
            }
            await websocket.send(json.dumps(resources_message))
            response = await websocket.recv()
            print(f"[TEST] 资源列表响应: {response}")
            
            print("\n[TEST] 所有测试完成！")
            
    except ConnectionRefusedError:
        print(f"[ERROR] 连接被拒绝，请确保MCP服务器正在运行在 {uri}")
    except Exception as e:
        print(f"[ERROR] 测试失败: {e}")


async def test_http_api():
    """测试HTTP API"""
    import requests
    
    base_url = "http://localhost:8000"
    
    try:
        print(f"\n[HTTP TEST] 测试HTTP API: {base_url}")
        
        # 测试健康检查
        print("[HTTP TEST] 测试健康检查")
        response = requests.get(f"{base_url}/health")
        print(f"[HTTP TEST] 健康检查响应: {response.status_code} - {response.json()}")
        
        # 测试工具列表
        print("[HTTP TEST] 测试工具列表")
        response = requests.get(f"{base_url}/api/tools")
        print(f"[HTTP TEST] 工具列表响应: {response.status_code} - {response.json()}")
        
        # 测试设备列表
        print("[HTTP TEST] 测试设备列表")
        response = requests.get(f"{base_url}/api/tools/device.list")
        print(f"[HTTP TEST] 设备列表响应: {response.status_code} - {response.json()}")
        
        print("[HTTP TEST] HTTP API测试完成！")
        
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] HTTP连接失败，请确保服务器正在运行在 {base_url}")
    except Exception as e:
        print(f"[ERROR] HTTP测试失败: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("MCP测试设备管理系统 - 客户端测试")
    print("=" * 60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 运行测试
    asyncio.run(test_mcp_server())
    asyncio.run(test_http_api())
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
