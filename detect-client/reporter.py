import requests
import json
import threading
import time
import os
import cv2
import base64
from events import EventLevel, EventTypeToString
from datetime import datetime, timedelta, timezone


try:
    from playsound import playsound
    PLAY_SOUND_AVAILABLE = True
except ImportError:
    PLAY_SOUND_AVAILABLE = False
    print("警告: 未安装playsound库，声音报警功能不可用")


class Reporter:
    """
    报告器类
    负责处理事件警报和上报到服务器
    """
    
    def __init__(self, config):
        """
        初始化报告器
        
        Args:
            config (Config): 配置管理器实例
        """
        self.config = config.get_server_config()
        self.last_report_time = {}  # 记录上次上报每种行为的时间，防止频繁上报
        self.report_interval = self.config.get('report_interval', 60)  # 默认60秒
        self.device_id=config.get_camera_config().get('device_id', '1')
        
        # 检查报警音文件是否存在
        self.alarm_sound_path = "alarm.wav"
        self.alarm_sound_available = PLAY_SOUND_AVAILABLE and os.path.exists(self.alarm_sound_path)
        if not self.alarm_sound_available and PLAY_SOUND_AVAILABLE:
            print(f"警告: 报警音文件 {self.alarm_sound_path} 不存在")
        
        # 添加音频播放状态跟踪
        self.is_playing_alarm = False
    
    def handle_events(self, events, frame):
        """
        处理事件列表
        
        Args:
            events (list): 行为事件列表
            frame (numpy.ndarray): 当前视频帧
        """
        for event in events:
            print(f"检测到行为事件: {event}")
            
            # 1. 播放警报音（在非阻塞线程中）
            if self.alarm_sound_available and not self.is_playing_alarm:
                threading.Thread(target=self._play_alarm, daemon=True).start()
                
            # 2. 上报服务器（在非阻塞线程中）
            threading.Thread(target=self._report_to_server, args=(event, frame), daemon=True).start()
            self._print_to_screen(event)

    def _play_alarm(self):
        """
        播放警报音
        """
        try:
            if self.alarm_sound_available:
                self.is_playing_alarm = True
                playsound(self.alarm_sound_path)
        except Exception as e:
            print(f"播放报警音失败: {e}")
        finally:
            self.is_playing_alarm = False

    def _report_to_server(self, event, frame):
        """
        上报事件到服务器
        
        Args:
            event (BehaviorEvent): 行为事件
            frame (numpy.ndarray): 当前视频帧
        """
        behavior_key = f"{event.type.__class__.__name__}_{event.type.name}"
        current_time = time.time()
        
        if behavior_key in self.last_report_time:
            if current_time - self.last_report_time[behavior_key] < self.report_interval:
                return
        
        _, img_encoded = cv2.imencode('.jpg', frame)
        img_base64 = base64.b64encode(img_encoded).decode('utf-8')
        
        event_dict = event.to_dict()
        event_type_converter = EventTypeToString()
        
        utc_time = datetime.fromtimestamp(event_dict["timestamp"], tz=timezone.utc)
        beijing_time = utc_time + timedelta(hours=8)
        
        server_event = {
            "driver_id": event_dict["driver_id"],
            "event_type": event_type_converter.get_event_type_string(event.type),
            "confidence": event_dict["confidence"],
            "timestamp": beijing_time.isoformat(),
            "image": img_base64
        }
        
        if "details" in event_dict and event_dict["details"]:
            server_event["details"] = event_dict["details"]
            
        payload = {
            "device_id": self.device_id,
            "events": [server_event]
        }
        
        headers = {
            "Content-Type": "application/json",
        }
        
        api_endpoint = self.config.get('api_endpoint', '')
        if not api_endpoint:
            print("错误: 未配置服务器API端点")
            return
        
        try:
            response = requests.post(
                api_endpoint,
                json=payload,
                headers=headers,
                timeout=self.config.get('timeout_seconds', 5)
            )
            
            if response.status_code in [200, 201]:
                print(f"成功上报 {behavior_key} 到服务器")
                self.last_report_time[behavior_key] = current_time
            else:
                print(f"上报 {behavior_key} 失败，状态码: {response.status_code}, 响应内容: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"上报到服务器时发生网络错误: {e}")
        except Exception as e:
            print(f"上报到服务器时发生未知错误: {e}")

    def _print_to_screen(self, event):
        """
        打印事件到屏幕
        """
        # 防频繁打印：同一种行为在指定时间间隔内只打印一次
        behavior_key = f"{event.type.__class__.__name__}_{event.type.name}"
        current_time = time.time()
        
        if behavior_key in self.last_report_time:
            if current_time - self.last_report_time[behavior_key] < self.report_interval:
                # 时间间隔未到，不重复打印
                return
        
        # 创建 EventTypeToString 实例
        event_type_converter = EventTypeToString()
        event_type_string = event_type_converter.get_event_type_string(event.type)
        
        # 将UTC时间戳转换为北京时间
        utc_time = datetime.fromtimestamp(event.timestamp, tz=timezone.utc)
        beijing_time = utc_time + timedelta(hours=8)
        print(f"{beijing_time.isoformat()}: {event_type_string}")
        self.last_report_time[behavior_key] = current_time