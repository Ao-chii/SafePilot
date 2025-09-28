import requests
import json
from datetime import datetime, timedelta
import time

# 测试服务器地址
BASE_URL = "http://localhost:5000/api/v1"

def test_create_events_success():
    """测试成功创建事件"""
    print("测试成功创建事件...")
    
    # 准备测试数据
    test_events = [
        {
            "driver_id": 2,
            "event_type": "疲劳驾驶",
            "confidence": 0.85,
            "timestamp": (datetime.utcnow() - timedelta(minutes=5)).isoformat()
        },
        {
            "driver_id": 2,
            "event_type": "抽烟",
            "confidence": 0.72,
            "timestamp": (datetime.utcnow() - timedelta(minutes=3)).isoformat(),
            "details": {"object": "phone"}
        }
    ]
    
    payload = {
        "device_id": 1,
        "events": test_events
    }
    
    # 发送POST请求
    response = requests.post(f"{BASE_URL}/events", 
                           json=payload)
    
    # 验证响应
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    
    if response.status_code == 201:
        data = response.json()
        print(f"成功创建 {len(data)} 个事件")
        print("测试成功!")
        return True
    else:
        print("测试失败!")
        return False

def test_create_events_missing_device_id():
    """测试缺少device_id时的错误处理"""
    print("\n测试缺少device_id时的错误处理...")
    
    payload = {
        "events": [
            {
                "driver_id": "driver001",
                "event_type": "drowsiness",
                "confidence": 0.85,
                "timestamp": datetime.utcnow().isoformat()
            }
        ]
    }
    
    response = requests.post(f"{BASE_URL}/events",
                           json=payload)
    
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    
    if response.status_code == 400:
        data = response.json()
        if 'device_id and events are required' in data.get('error', ''):
            print("测试成功!")
            return True
    
    print("测试失败!")
    return False

def test_create_events_missing_events():
    """测试缺少events时的错误处理"""
    print("\n测试缺少events时的错误处理...")
    
    payload = {
        "device_id": "device001"
    }
    
    response = requests.post(f"{BASE_URL}/events",
                           json=payload)
    
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    
    if response.status_code == 400:
        data = response.json()
        if 'device_id and events are required' in data.get('error', ''):
            print("测试成功!")
            return True
    
    print("测试失败!")
    return False

def test_create_events_invalid_events_format():
    """测试events不是数组时的错误处理"""
    print("\n测试events不是数组时的错误处理...")
    
    payload = {
        "device_id": "device001",
        "events": "invalid_format"
    }
    
    response = requests.post(f"{BASE_URL}/events",
                           json=payload)
    
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    
    if response.status_code == 400:
        data = response.json()
        if 'events must be an array' in data.get('error', ''):
            print("测试成功!")
            return True
    
    print("测试失败!")
    return False

def test_create_events_missing_required_fields():
    """测试事件缺少必填字段时的错误处理"""
    print("\n测试事件缺少必填字段时的错误处理...")
    
    payload = {
        "device_id": "device001",
        "events": [
            {
                "driver_id": "driver001",
                "event_type": "drowsiness"
                # 缺少confidence和timestamp
            }
        ]
    }
    
    response = requests.post(f"{BASE_URL}/events",
                           json=payload)
    
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    
    if response.status_code == 400:
        data = response.json()
        if 'Missing required field' in data.get('error', ''):
            print("测试成功!")
            return True
    
    print("测试失败!")
    return False

def test_create_events_invalid_timestamp_format():
    """测试时间戳格式错误时的处理"""
    print("\n测试时间戳格式错误时的处理...")
    
    payload = {
        "device_id": "device001",
        "events": [
            {
                "driver_id": "driver001",
                "event_type": "drowsiness",
                "confidence": 0.85,
                "timestamp": "invalid-timestamp-format"
            }
        ]
    }
    
    response = requests.post(f"{BASE_URL}/events",
                           json=payload)
    
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
    
    if response.status_code == 400:
        data = response.json()
        if 'Invalid timestamp format' in data.get('error', ''):
            print("测试成功!")
            return True
    
    print("测试失败!")
    return False

def main():
    """主函数，运行所有测试"""
    print("开始测试事件创建功能...")
    print("=" * 50)
    
    # 等待服务器启动
    time.sleep(2)
    
    tests = [
        test_create_events_success,
        # test_create_events_missing_device_id,
        # test_create_events_missing_events,
        # test_create_events_invalid_events_format,
        # test_create_events_missing_required_fields,
        # test_create_events_invalid_timestamp_format
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"测试执行出错: {e}")
    
    print("\n" + "=" * 50)
    print(f"测试完成: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("所有测试都通过了!")
    else:
        print(f"有 {total - passed} 个测试失败")

if __name__ == "__main__":
    main()