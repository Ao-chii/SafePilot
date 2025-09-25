"""打哈欠检测器模块
负责检测驾驶员打哈欠行为
"""

import cv2
import numpy as np
from collections import deque
import time
from events import EventLevel, DangerousBehavior, BehaviorEvent
from .base_detector import BaseDetector


class YawningDetector(BaseDetector):
    """
    打哈欠检测器类
    通过检测嘴部关键点的长宽比来判断是否在打哈欠
    """
    
    def __init__(self, config):
        """
        初始化打哈欠检测器
        
        Args:
            config (Config): 配置管理器实例
        """
        super().__init__(config)
        # 嘴部关键点索引
        self.MOUTH_LANDMARKS = [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291,
                               78, 95, 88, 178, 87, 14, 317, 402, 318, 324, 308]
        # 上唇关键点
        self.UPPER_LIP_LANDMARKS = [78, 191, 80, 81, 82, 13, 312, 311, 310, 415, 308]
        # 下唇关键点
        self.LOWER_LIP_LANDMARKS = [78, 95, 88, 178, 87, 14, 317, 402, 318, 324, 308]
        
        # 用于状态跟踪的变量
        self.yawn_deque = deque(maxlen=90)  # 记录最近90帧的嘴部状态（假设30FPS，约3秒）
        self.last_yawn_time = time.time()
    
    def detect(self, yolo_detections, mediapipe_results, frame=None):
        """
        检测打哈欠行为
        
        Args:
            yolo_detections (list): YOLO检测结果
            mediapipe_results (dict): MediaPipe分析结果
            frame: 当前视频帧（可选，用于在视频中显示信息）
            
        Returns:
            list: 检测到的行为事件列表
        """
        events = []
        self._detect_yawning(events, mediapipe_results, frame)
        return events
    
    def _detect_yawning(self, events, mediapipe_results, frame=None):
        """
        检测打哈欠行为
        
        Args:
            events (list): 事件列表
            mediapipe_results (dict): MediaPipe分析结果
            frame: 视频帧（可选，用于显示疲劳信息）
        """
        if not mediapipe_results['face'].multi_face_landmarks:
            # 在视频画面中显示未检测到面部
            if frame is not None:
                cv2.putText(frame, "No face detected", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            return
        
        # 获取面部关键点
        face_landmarks = mediapipe_results['face'].multi_face_landmarks[0]
        
        # 计算嘴部的长宽比
        mar = self._calculate_mouth_aspect_ratio(face_landmarks)
        
        # 判断是否在打哈欠
        yawn_threshold = self.behavior_rules.get('yawn_threshold', 0.6)
        is_yawning = mar > yawn_threshold
        self.yawn_deque.append(is_yawning)
        
        # 在视频画面中绘制嘴部关键点以便测试
        if frame is not None:
            self._draw_mouth_landmarks(frame, face_landmarks)
        
        # 计算过去N秒内打哈欠的帧所占的比例
        yawn_time_window = self.behavior_rules.get('yawn_time_window', 3.0)
        time_window_frames = int(yawn_time_window * 30)  # 假设30FPS
        recent_deque = list(self.yawn_deque)[-time_window_frames:]
        
        if len(recent_deque) > 0:
            yawn_ratio = sum(recent_deque) / len(recent_deque)
            yawn_ratio_threshold = self.behavior_rules.get('yawn_ratio_threshold', 0.1)
            
            # 在视频画面中显示打哈欠警告
            if frame is not None and yawn_ratio > yawn_ratio_threshold and is_yawning:
                cv2.putText(frame, "YAWNING DETECTED!", (10, 120), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # 当yawn_ratio超过阈值且当前正在打哈欠时检测到打哈欠行为
            if yawn_ratio > yawn_ratio_threshold and is_yawning:
                # 检测到打哈欠
                confidence = round(max(yawn_ratio, 0.6), 2)  # 确保最小置信度，并保留两位小数
                event = BehaviorEvent(
                    driver_id=1,
                    event_type=DangerousBehavior.YAWNING,
                    confidence=confidence,
                    timestamp=time.time(),
                    details={
                        'mar': round(float(mar), 2),           # 保留两位小数
                        'yawn_ratio': round(float(yawn_ratio), 2),  # 保留两位小数
                        'mouth_state': 'yawning' if is_yawning else 'normal'
                    }
                )
                events.append(event)
    
    def _draw_mouth_landmarks(self, frame, face_landmarks):
        """
        在视频帧上绘制嘴部关键点，便于测试和调试
        
        Args:
            frame: 视频帧
            face_landmarks: 面部关键点
        """
        height, width = frame.shape[:2]
        
        # 绘制嘴部关键点
        for idx in self.MOUTH_LANDMARKS:
            landmark = face_landmarks.landmark[idx]
            x = int(landmark.x * width)
            y = int(landmark.y * height)
            cv2.circle(frame, (x, y), 2, (0, 255, 255), -1)  # 黄色点表示嘴部关键点
    
    def _calculate_mouth_aspect_ratio(self, face_landmarks):
        """
        计算嘴部长宽比(MAR)
        
        Args:
            face_landmarks: 面部关键点
            
        Returns:
            float: 嘴部长宽比
        """
        if not face_landmarks:
            return 0.0
        
        try:
            # 获取上唇和下唇的关键点
            upper_lip_points = []
            lower_lip_points = []
            
            for idx in self.UPPER_LIP_LANDMARKS:
                landmark = face_landmarks.landmark[idx]
                upper_lip_points.append(np.array([landmark.x, landmark.y]))
            
            for idx in self.LOWER_LIP_LANDMARKS:
                landmark = face_landmarks.landmark[idx]
                lower_lip_points.append(np.array([landmark.x, landmark.y]))
            
            # 计算上下唇之间的垂直距离
            vertical_distances = []
            for i in range(len(upper_lip_points)):
                distance = np.linalg.norm(upper_lip_points[i] - lower_lip_points[i])
                vertical_distances.append(distance)
            
            # 计算水平距离（嘴部宽度）
            left_mouth_point = face_landmarks.landmark[61]  # 嘴巴左边
            right_mouth_point = face_landmarks.landmark[291]  # 嘴巴右边
            horizontal_distance = np.linalg.norm(
                np.array([left_mouth_point.x, left_mouth_point.y]) - 
                np.array([right_mouth_point.x, right_mouth_point.y])
            )
            
            # 防止除零错误
            if horizontal_distance == 0:
                return 0.0
            
            # 计算MAR (Mouth Aspect Ratio)
            avg_vertical_distance = np.mean(vertical_distances)
            mar = avg_vertical_distance / horizontal_distance
            return mar
        except:
            return 0.0