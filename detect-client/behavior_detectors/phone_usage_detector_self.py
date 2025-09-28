"""手机使用检测器模块
负责检测驾驶员使用手机的行为
"""

import cv2
import numpy as np
import time
from events import EventLevel, DangerousBehavior, BehaviorEvent
from .base_detector import BaseDetector


class PhoneUsageDetector(BaseDetector):
    """
    手机使用检测器类
    通过检测自己训练的YOLO模型来判断是否在使用手机
    """
    
    def __init__(self, config):
        """
        初始化手机使用检测器
        
        Args:
            config (Config): 配置管理器实例
        """
        super().__init__(config)
    
    def detect(self, self_yolo_detections, frame=None):
        """
        检测手机使用行为
        
        Args:
            self_yolo_detections (list): 自己训练的YOLO模型检测结果
            frame: 当前视频帧（可选，用于在视频中显示信息）
            
        Returns:
            list: 检测到的行为事件列表
        """
        events = []
        self._detect_phone_usage(events, self_yolo_detections, frame)
        return events
    
    def _detect_phone_usage(self, events, self_yolo_detections, frame=None):
        """
        检测手机使用行为
        
        Args:
            events (list): 事件列表
            self_yolo_detections (list): 自己训练的YOLO模型检测结果
            frame: 视频帧（可选，用于显示检测信息）
        """
        # 检查是否检测到手机使用行为 (class_id=4 根据配置文件)
        phone_usage_detections = [det for det in self_yolo_detections if det['class_id'] == 4]
        
        if not phone_usage_detections:
            return  # 如果没有检测到手机使用行为，则直接返回
        
        # 获取置信度最高的手机使用检测结果
        phone_usage_detection = max(phone_usage_detections, key=lambda x: x['confidence'])
        phone_usage_confidence = phone_usage_detection['confidence']
        
        # 添加手机使用事件
        event = BehaviorEvent(
            event_type=DangerousBehavior.PHONE_READING,
            confidence=float(phone_usage_confidence),  # 确保转换为Python原生类型
            timestamp=time.time(),
            details={
                'phone_usage_confidence': round(float(phone_usage_confidence), 2)
            }
        )
        events.append(event)
        
        # 在视频画面中显示手机使用检测信息
        if frame is not None:
            # 绘制检测框
            x1, y1, x2, y2 = phone_usage_detection['bbox']
            # 确保坐标是整数类型
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # 显示标签和置信度
            label = f"Phone Usage: {phone_usage_confidence:.2f}"
            cv2.putText(frame, label, (x1, y1 - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)