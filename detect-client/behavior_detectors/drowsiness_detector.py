"""疲劳驾驶检测器模块
负责检测驾驶员的疲劳状态
"""

import cv2
import numpy as np
from collections import deque
import time
from events import EventLevel, DangerousBehavior, BehaviorEvent
from .base_detector import BaseDetector


class DrowsinessDetector(BaseDetector):
    """
    疲劳驾驶检测器类
    使用PERCLOS方法检测驾驶员疲劳状态
    """
    
    def __init__(self, config):
        """
        初始化疲劳驾驶检测器
        
        Args:
            config (Config): 配置管理器实例
        """
        super().__init__(config)
        # 用于状态跟踪的变量
        self.eye_close_deque = deque(maxlen=90)  # 记录最近90帧的眼睛状态（假设30FPS，约3秒）
        self.last_eyes_open_time = time.time()
    
    def detect(self, yolo_detections, mediapipe_results, frame=None):
        """
        检测疲劳驾驶行为
        
        Args:
            yolo_detections (list): YOLO检测结果
            mediapipe_results (dict): MediaPipe分析结果
            frame: 当前视频帧（可选，用于在视频中显示信息）
            
        Returns:
            list: 检测到的行为事件列表
        """
        events = []
        self._detect_drowsiness(events, mediapipe_results, frame)
        return events
    
    def _detect_drowsiness(self, events, mediapipe_results, frame=None):
        """
        检测疲劳驾驶行为（PERCLOS方法）
        
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
        
        # 计算双眼的EAR值
        left_eye_ear = self._calculate_eye_aspect_ratio(face_landmarks, 
                                                       self._get_left_eye_indices())
        right_eye_ear = self._calculate_eye_aspect_ratio(face_landmarks, 
                                                        self._get_right_eye_indices())
        avg_ear = (left_eye_ear + right_eye_ear) / 2.0
        
        # 判断眼睛是否闭合
        eyes_close_threshold = self.behavior_rules.get('eyes_close_threshold', 0.21)
        is_eyes_closed = avg_ear < eyes_close_threshold
        self.eye_close_deque.append(is_eyes_closed)
        
        # 在视频画面中绘制眼部关键点以便测试
        if frame is not None:
            self._draw_eye_landmarks(frame, face_landmarks)
        
        # 计算过去N秒内眼睛闭合的帧所占的比例 (PERCLOS)
        perclos_time_window = self.behavior_rules.get('perclos_time_window', 3.0)
        time_window_frames = int(perclos_time_window * 30)  # 假设30FPS
        recent_deque = list(self.eye_close_deque)[-time_window_frames:]
        
        if len(recent_deque) > 0:
            perclos = sum(recent_deque) / len(recent_deque)
            perclos_threshold = self.behavior_rules.get('perclos_threshold', 0.5)
            
            # 在视频画面中显示疲劳相关信息
            if frame is not None:
                # 显示PERCLOS值
                cv2.putText(frame, f"PERCLOS: {perclos:.2f}", (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                # 显示眼睛状态（睁开/闭合）
                eye_state = "CLOSED" if is_eyes_closed else "OPEN"
                color = (0, 0, 255) if is_eyes_closed else (0, 255, 0)
                cv2.putText(frame, f"Eyes: {eye_state}", (10, 90), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                # 显示疲劳警告
                if perclos > perclos_threshold and (is_eyes_closed or avg_ear < 0.2):
                    cv2.putText(frame, "DROWSINESS DETECTED!", (10, 120), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # 当perclos超过阈值时检测到严重疲劳
            # 或者当眼睛闭合且EAR值非常小时检测到疲劳（即时检测）
            if perclos > perclos_threshold and (is_eyes_closed or avg_ear < 0.2):
                # 检测到严重疲劳
                confidence = round(max(perclos, 0.5), 2)  # 确保最小置信度，并保留两位小数
                event = BehaviorEvent(
                    event_type=DangerousBehavior.SEVERE_DROWSINESS,
                    confidence=confidence,
                    timestamp=time.time(),
                    details={
                        'perclos': round(float(perclos), 2),  # 保留两位小数
                        'ear': round(float(avg_ear), 2),      # 保留两位小数
                        'eye_state': 'closed' if is_eyes_closed else 'open'
                    }
                )
                events.append(event)
    
    def _draw_eye_landmarks(self, frame, face_landmarks):
        """
        在视频帧上绘制眼部关键点，便于测试和调试
        
        Args:
            frame: 视频帧
            face_landmarks: 面部关键点
        """
        height, width = frame.shape[:2]
        
        # 绘制左眼关键点
        for idx in self._get_left_eye_indices():
            landmark = face_landmarks.landmark[idx]
            x = int(landmark.x * width)
            y = int(landmark.y * height)
            cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)
        
        # 绘制右眼关键点
        for idx in self._get_right_eye_indices():
            landmark = face_landmarks.landmark[idx]
            x = int(landmark.x * width)
            y = int(landmark.y * height)
            cv2.circle(frame, (x, y), 2, (255, 0, 0), -1)
    
    def _calculate_eye_aspect_ratio(self, face_landmarks, eye_indices):
        """
        计算眼睛长宽比(EAR)
        
        Args:
            face_landmarks: 面部关键点
            eye_indices: 眼部关键点索引
            
        Returns:
            float: 眼睛长宽比
        """
        if not face_landmarks or len(eye_indices) < 6:
            return 0.0
        
        # 获取眼部关键点坐标
        eye_points = []
        for idx in eye_indices:
            landmark = face_landmarks.landmark[idx]
            # 将归一化的坐标保存为numpy数组
            eye_points.append(np.array([landmark.x, landmark.y]))
        
        # 计算EAR
        try:
            # 垂直距离
            vertical_1 = np.linalg.norm(eye_points[1] - eye_points[5])
            vertical_2 = np.linalg.norm(eye_points[2] - eye_points[4])
            
            # 水平距离
            horizontal = np.linalg.norm(eye_points[0] - eye_points[3])
            
            # 防止除零错误
            if horizontal == 0:
                return 0.0
            
            # 计算EAR
            ear = (vertical_1 + vertical_2) / (2.0 * horizontal)
            return ear
        except:
            return 0.0
    
    @staticmethod
    def _get_left_eye_indices():
        """
        获取左眼关键点索引
        
        Returns:
            list: 左眼关键点索引列表
        """
        return [362, 385, 387, 263, 373, 380]  # 左眼关键点
    
    @staticmethod
    def _get_right_eye_indices():
        """
        获取右眼关键点索引
        
        Returns:
            list: 右眼关键点索引列表
        """
        return [33, 160, 158, 133, 153, 144]  # 右眼关键点