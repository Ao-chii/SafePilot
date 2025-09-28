"""喝水检测器模块
负责检测驾驶员喝水的行为
"""

import cv2
import numpy as np
import time
from events import EventLevel, WarningBehavior, BehaviorEvent
from .base_detector import BaseDetector


class DrinkingDetector(BaseDetector):
    """
    喝水检测器类
    通过检测自己训练的YOLO模型来判断是否在喝水
    """
    
    def __init__(self, config):
        """
        初始化喝水检测器
        
        Args:
            config (Config): 配置管理器实例
        """
        super().__init__(config)
    
    def detect(self, self_yolo_detections, frame=None):
        """
        检测喝水行为
        
        Args:
            self_yolo_detections (list): 自己训练的YOLO模型检测结果
            frame: 当前视频帧（可选，用于在视频中显示信息）
            
        Returns:
            list: 检测到的行为事件列表
        """
        events = []
        self._detect_drinking(events, self_yolo_detections, frame)
        return events
    
    def _detect_drinking(self, events, self_yolo_detections, frame=None):
        """
        检测喝水行为
        
        Args:
            events (list): 事件列表
            self_yolo_detections (list): 自己训练的YOLO模型检测结果
            frame: 视频帧（可选，用于显示检测信息）
        """
        # 检查是否检测到喝水行为 (class_id=1 根据配置文件)
        drinking_detections = [det for det in self_yolo_detections if det['class_id'] == 1 or det['class_id'] == 3]
        
        if not drinking_detections:
            return  # 如果没有检测到喝水行为，则直接返回
        
        # 获取置信度最高的喝水检测结果
        drinking_detection = max(drinking_detections, key=lambda x: x['confidence'])
        drinking_confidence = drinking_detection['confidence']
        
        # 添加喝水事件
        event = BehaviorEvent(
            event_type=WarningBehavior.EATING_DRINKING,
            confidence=float(drinking_confidence),  # 确保转换为Python原生类型
            timestamp=time.time(),
            details={
                'drinking_confidence': round(float(drinking_confidence), 2)
            }
        )
        events.append(event)
        
        # 在视频画面中显示喝水检测信息
        if frame is not None:
            # 绘制检测框
            x1, y1, x2, y2 = drinking_detection['bbox']
            # 确保坐标是整数类型
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # 显示标签和置信度
            label = f"Drinking: {drinking_confidence:.2f}"
            cv2.putText(frame, label, (x1, y1 - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)