# 数据上传模块 - 将检测到的事件上报到服务器

import os
import json
import time
import logging
import threading
import queue
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Tuple

from client.analyzer import BehaviorObserver, BehaviorType
from client.config import config, DATA_DIR

logger = logging.getLogger("SafePilot.DataUploader")

# 创建数据缓存目录
CACHE_DIR = DATA_DIR / "cache"
os.makedirs(CACHE_DIR, exist_ok=True)


class DataUploader(BehaviorObserver):
    """数据上传器 - 观察者模式，接收行为分析器的通知，上传数据到服务器"""
    
    def __init__(self):
        """初始化数据上传器"""
        self.config = config.upload
        self.server_url = config.server_url
        self.device_id = config.device_id
        self.driver_id = config.driver_id
        
        # 上传配置
        self.enabled = self.config["enabled"]
        self.upload_interval = self.config["upload_interval"]
        self.retry_interval = self.config["retry_interval"]
        self.max_retries = self.config["max_retries"]
        self.buffer_size = self.config["buffer_size"]
        
        # 数据队列
        self.event_queue = queue.Queue(maxsize=self.buffer_size)
        
        # 上传状态
        self.last_upload_time = 0
        self.is_uploading = False
        self.upload_success_count = 0
        self.upload_fail_count = 0
        self.retry_count = 0
        
        # 线程和锁
        self.upload_thread = None
        self.is_running = False
        self.lock = threading.RLock()
        
        # 加载本地缓存
        self._load_cached_events()
        
        # 启动上传线程
        if self.enabled:
            self._start_upload_thread()
        
        logger.info(f"DataUploader初始化完成，上传服务器: {self.server_url}")
    
    def on_behavior_detected(self, behavior_type: str, confidence: float, details: Dict[str, Any]) -> None:
        """
        接收行为检测通知并添加到上传队列
        
        Args:
            behavior_type: 行为类型
            confidence: 置信度
            details: 详细信息
        """
        if not self.enabled:
            return
        
        # 创建事件数据
        event = {
            "device_id": self.device_id,
            "driver_id": self.driver_id,
            "event_type": behavior_type,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        
        # 添加到上传队列
        try:
            if self.event_queue.full():
                # 队列已满，移除最早的事件
                try:
                    self.event_queue.get_nowait()
                except queue.Empty:
                    pass
            
            self.event_queue.put_nowait(event)
            logger.debug(f"事件已添加到上传队列: {behavior_type}")
            
            # 如果需要立即上传危险行为
            if behavior_type in [BehaviorType.DROWSY, BehaviorType.PHONE_USE] and confidence > 0.8:
                self._trigger_immediate_upload()
            
        except Exception as e:
            logger.error(f"添加事件到队列失败: {e}")
    
    def _start_upload_thread(self) -> None:
        """启动上传线程"""
        if self.upload_thread is not None and self.upload_thread.is_alive():
            return
        
        self.is_running = True
        self.upload_thread = threading.Thread(target=self._upload_loop, daemon=True)
        self.upload_thread.start()
        logger.info("上传线程已启动")
    
    def _upload_loop(self) -> None:
        """上传循环"""
        while self.is_running:
            try:
                # 检查是否到达上传间隔
                current_time = time.time()
                if current_time - self.last_upload_time >= self.upload_interval:
                    self._upload_events()
                
                # 休眠一段时间
                time.sleep(1.0)
            
            except Exception as e:
                logger.error(f"上传循环发生错误: {e}")
                time.sleep(5.0)  # 出错后等待较长时间
    
    def _trigger_immediate_upload(self) -> None:
        """触发立即上传"""
        threading.Thread(target=self._upload_events, daemon=True).start()
    
    def _upload_events(self) -> bool:
        """
        上传事件数据
        
        Returns:
            bool: 上传是否成功
        """
        with self.lock:
            if self.is_uploading:
                return False
            
            self.is_uploading = True
        
        success = False
        
        try:
            # 收集队列中的所有事件
            events = []
            while not self.event_queue.empty():
                try:
                    event = self.event_queue.get_nowait()
                    events.append(event)
                except queue.Empty:
                    break
            
            # 如果没有事件，直接返回
            if not events:
                self.is_uploading = False
                return True
            
            # 上传数据
            if self._send_events_to_server(events):
                # 上传成功
                self.upload_success_count += 1
                self.last_upload_time = time.time()
                self.retry_count = 0
                success = True
                logger.info(f"成功上传{len(events)}条事件数据")
            else:
                # 上传失败，缓存到本地
                self.upload_fail_count += 1
                self.retry_count += 1
                self._cache_events(events)
                
                # 计算下次重试时间（指数退避）
                retry_time = min(self.retry_interval * (2 ** (self.retry_count - 1)), 300)  # 最长5分钟
                logger.warning(f"上传失败，{retry_time}秒后重试，已缓存{len(events)}条事件")
        
        except Exception as e:
            logger.error(f"上传事件数据时发生错误: {e}")
            self.upload_fail_count += 1
            self.retry_count += 1
        
        finally:
            self.is_uploading = False
            return success
    
    def _send_events_to_server(self, events: List[Dict[str, Any]]) -> bool:
        """
        发送事件数据到服务器
        
        Args:
            events: 事件数据列表
            
        Returns:
            bool: 是否发送成功
        """
        if not self.server_url:
            logger.error("服务器URL未配置")
            return False
        
        try:
            # 构建请求数据
            data = {
                "device_id": self.device_id,
                "events": events,
                "timestamp": datetime.now().isoformat(),
                "batch_id": f"{self.device_id}_{int(time.time())}"
            }
            
            # 发送请求
            endpoint = f"{self.server_url}/api/events"
            
            # 设置超时和重试
            for attempt in range(self.max_retries):
                try:
                    response = requests.post(
                        endpoint,
                        json=data,
                        timeout=10,
                        headers={"Content-Type": "application/json"}
                    )
                    
                    if response.status_code == 200:
                        return True
                    
                    logger.warning(f"上传失败，状态码: {response.status_code}")
                    
                    # 如果服务器返回429 (Too Many Requests)，等待较长时间
                    if response.status_code == 429:
                        time.sleep(5 * (attempt + 1))
                    else:
                        time.sleep(1 * (attempt + 1))
                
                except requests.RequestException as e:
                    logger.error(f"请求异常: {e}")
                    time.sleep(2 * (attempt + 1))
            
            return False
        
        except Exception as e:
            logger.error(f"发送数据到服务器时发生错误: {e}")
            return False
    
    def _cache_events(self, events: List[Dict[str, Any]]) -> bool:
        """
        缓存事件到本地
        
        Args:
            events: 事件数据列表
            
        Returns:
            bool: 是否缓存成功
        """
        try:
            # 生成缓存文件名
            timestamp = int(time.time())
            cache_file = CACHE_DIR / f"events_{timestamp}.json"
            
            # 保存到文件
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(events, f)
            
            logger.info(f"事件已缓存到本地: {cache_file}")
            return True
        
        except Exception as e:
            logger.error(f"缓存事件到本地失败: {e}")
            return False
    
    def _load_cached_events(self) -> None:
        """加载本地缓存的事件数据"""
        try:
            # 查找所有缓存文件
            cache_files = list(CACHE_DIR.glob("events_*.json"))
            if not cache_files:
                return
            
            logger.info(f"发现{len(cache_files)}个缓存事件文件")
            
            # 加载事件并添加到队列
            for cache_file in sorted(cache_files):
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        events = json.load(f)
                    
                    # 添加到队列
                    for event in events:
                        if not self.event_queue.full():
                            self.event_queue.put(event)
                        else:
                            break
                    
                    # 删除缓存文件
                    os.remove(cache_file)
                    
                except Exception as e:
                    logger.error(f"加载缓存文件失败: {cache_file}, 错误: {e}")
            
            logger.info("缓存事件加载完成")
        
        except Exception as e:
            logger.error(f"加载缓存事件时发生错误: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取上传状态
        
        Returns:
            Dict[str, Any]: 状态信息
        """
        return {
            "enabled": self.enabled,
            "server_url": self.server_url,
            "queue_size": self.event_queue.qsize(),
            "is_uploading": self.is_uploading,
            "success_count": self.upload_success_count,
            "fail_count": self.upload_fail_count,
            "retry_count": self.retry_count,
            "last_upload_time": self.last_upload_time
        }
    
    def shutdown(self) -> None:
        """关闭数据上传器"""
        with self.lock:
            self.is_running = False
            
            # 尝试最后一次上传
            if self.event_queue.qsize() > 0:
                self._upload_events()
            
            if self.upload_thread and self.upload_thread.is_alive():
                self.upload_thread.join(timeout=5.0)


# 创建全局实例
data_uploader = DataUploader()


if __name__ == "__main__":
    # 测试代码
    import time
    
    # 测试上传器
    uploader = data_uploader
    
    # 禁用实际上传
    uploader.server_url = "http://localhost:5000"  # 使用本地测试服务器
    
    # 添加测试事件
    for i in range(5):
        uploader.on_behavior_detected(
            BehaviorType.EYES_CLOSED,
            0.9,
            {"test_id": i, "duration": 2.5}
        )
        print(f"添加测试事件 {i}")
        time.sleep(0.5)
    
    # 触发立即上传
    uploader._trigger_immediate_upload()
    print("触发上传")
    
    # 显示状态
    time.sleep(2)
    print(f"上传状态: {uploader.get_status()}")
    
    # 关闭
    uploader.shutdown()
    print("测试完成")
