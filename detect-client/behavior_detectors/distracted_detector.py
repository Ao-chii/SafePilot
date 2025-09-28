"""视线偏移检测器模块
负责检测驾驶员视线是否长时间偏移，包括长时间低头、转头等行为
"""

import cv2
import numpy as np
import time
from collections import deque
from events import EventLevel, DangerousBehavior, BehaviorEvent
from .base_detector import BaseDetector


class DistractedDetector(BaseDetector):
    """
    驾驶员分心检测器类（简化版）
    只检测长时间低头和转头两种情况
    """
    
    def __init__(self, config):
        """
        初始化视线偏移检测器
        
        Args:
            config (Config): 配置管理器实例
        """
        super().__init__(config)
        
        # 视线偏移检测参数
        self.PITCH_DOWN_THRESHOLD = 10  # 低头阈值
        self.YAW_THRESHOLD = 2          # 转头阈值
        
        # 时间阈值（秒）
        self.GAZE_DISTRACTED_THRESHOLD = 3.0  # 默认3秒
        
        # 状态跟踪变量
        self.pitch_down_start_time = None
        self.yaw_left_start_time = None
        self.yaw_right_start_time = None
        
        self.pitch_down_duration = 0
        self.yaw_left_duration = 0
        self.yaw_right_duration = 0
        
        # 上次触发事件的时间
        self.last_event_time = 0
        
    def detect(self, yolo_detections, mediapipe_results, frame=None):
        """
        检测视线偏移行为
        
        Args:
            yolo_detections (list): YOLO检测结果
            mediapipe_results (dict): MediaPipe分析结果
            frame: 当前视频帧（可选，用于在视频中显示信息）
            
        Returns:
            list: 检测到的行为事件列表
        """
        events = []
        
        # 检查是否有面部关键点数据
        if not mediapipe_results['face'].multi_face_landmarks:
            return events
            
        # 获取面部关键点
        face_landmarks = mediapipe_results['face'].multi_face_landmarks[0]
        
        # 获取图像尺寸
        if frame is not None:
            image_shape = frame.shape
        else:
            # 如果没有帧，使用默认尺寸
            image_shape = (480, 640, 3)
        
        # 计算俯仰角和偏航角（简化方法）
        pitch, yaw = self._calculate_head_angles(face_landmarks, image_shape)
        
        # 更新状态并检测事件
        current_time = time.time()
        self._update_state_and_detect_events(events, pitch, yaw, current_time)
        
        # 在视频画面中可视化结果
        if frame is not None:
            self._visualize_results(frame, pitch, yaw)
        
        return events
    
    def _calculate_head_angles(self, face_landmarks, image_shape):
        """
        简化方法计算头部角度
        
        Args:
            face_landmarks: 面部关键点
            image_shape: 图像尺寸
            
        Returns:
            tuple: (pitch, yaw) 俯仰角和偏航角
        """
        height, width = image_shape[:2]
        
        # 获取关键点
        nose_tip = face_landmarks.landmark[1]      # 鼻尖
        chin = face_landmarks.landmark[152]        # 下巴
        left_eye = face_landmarks.landmark[33]     # 左眼
        right_eye = face_landmarks.landmark[263]   # 右眼
        
        # 计算俯仰角（通过鼻尖和下巴的垂直位置差异）
        nose_y = nose_tip.y * height
        chin_y = chin.y * height
        pitch = chin_y - nose_y  # 下巴相对鼻尖越低，值越小（负值表示低头）
        
        # 计算偏航角（通过左右眼的水平位置差异）
        left_eye_x = left_eye.x * width
        right_eye_x = right_eye.x * width
        eye_distance = abs(left_eye_x - right_eye_x)
        
        # 简单估算：如果一只眼睛明显比另一只眼睛更靠近中线，则认为是转头
        face_center_x = (nose_tip.x + chin.x) * width / 2
        yaw = (left_eye_x + right_eye_x) / 2 - face_center_x
        
        # 归一化（简化处理）
        normalized_pitch = (pitch / height) * 100
        normalized_yaw = (yaw / width) * 100
        
        return normalized_pitch, normalized_yaw
    
    def _update_state_and_detect_events(self, events, pitch, yaw, current_time):
        """
        更新状态并检测事件
        
        Args:
            events (list): 事件列表
            pitch (float): 俯仰角
            yaw (float): 偏航角
            current_time (float): 当前时间戳
        """
        # 检查是否低头
        is_pitch_down = pitch < self.PITCH_DOWN_THRESHOLD
        
        # 检查是否左转头或右转头
        is_yaw_left = yaw < -self.YAW_THRESHOLD
        is_yaw_right = yaw > self.YAW_THRESHOLD
        
        # 更新低头状态
        if is_pitch_down:
            if self.pitch_down_start_time is None:
                self.pitch_down_start_time = current_time
            else:
                self.pitch_down_duration = current_time - self.pitch_down_start_time
        else:
            self.pitch_down_start_time = None
            self.pitch_down_duration = 0
        
        # 更新左转头状态
        if is_yaw_left:
            if self.yaw_left_start_time is None:
                self.yaw_left_start_time = current_time
            else:
                self.yaw_left_duration = current_time - self.yaw_left_start_time
        else:
            self.yaw_left_start_time = None
            self.yaw_left_duration = 0
        
        # 更新右转头状态
        if is_yaw_right:
            if self.yaw_right_start_time is None:
                self.yaw_right_start_time = current_time
            else:
                self.yaw_right_duration = current_time - self.yaw_right_start_time
        else:
            self.yaw_right_start_time = None
            self.yaw_right_duration = 0
        
        # 检测事件
        gaze_off_road_threshold = self.behavior_rules.get('gaze_off_road_threshold', 
                                                         self.GAZE_DISTRACTED_THRESHOLD)
        
        # 检查是否触发低头事件
        if self.pitch_down_duration >= gaze_off_road_threshold:
            if current_time - self.last_event_time > gaze_off_road_threshold:
                confidence = min(0.5 + (self.pitch_down_duration / 10.0), 1.0)
                event = BehaviorEvent(
                    event_type=DangerousBehavior.GAZE_OFF_ROAD,
                    confidence=round(confidence, 2),
                    timestamp=current_time,
                    details={
                        'type': 'looking_down',
                        'pitch': round(float(pitch), 2),
                        'duration': round(float(self.pitch_down_duration), 2)
                    }
                )
                events.append(event)
                self.last_event_time = current_time
        
        # 检查是否触发左转头事件
        elif self.yaw_left_duration >= gaze_off_road_threshold:
            if current_time - self.last_event_time > gaze_off_road_threshold:
                confidence = min(0.5 + (self.yaw_left_duration / 10.0), 1.0)
                event = BehaviorEvent(
                    event_type=DangerousBehavior.GAZE_OFF_ROAD,
                    confidence=round(confidence, 2),
                    timestamp=current_time,
                    details={
                        'type': 'turning_left',
                        'yaw': round(float(yaw), 2),
                        'duration': round(float(self.yaw_left_duration), 2)
                    }
                )
                events.append(event)
                self.last_event_time = current_time
        
        # 检查是否触发右转头事件
        elif self.yaw_right_duration >= gaze_off_road_threshold:
            if current_time - self.last_event_time > gaze_off_road_threshold:
                confidence = min(0.5 + (self.yaw_right_duration / 10.0), 1.0)
                event = BehaviorEvent(
                    event_type=DangerousBehavior.GAZE_OFF_ROAD,
                    confidence=round(confidence, 2),
                    timestamp=current_time,
                    details={
                        'type': 'turning_right',
                        'yaw': round(float(yaw), 2),
                        'duration': round(float(self.yaw_right_duration), 2)
                    }
                )
                events.append(event)
                self.last_event_time = current_time
    
    def _visualize_results(self, frame, pitch, yaw):
        """
        在视频帧上可视化检测结果
        
        Args:
            frame: 视频帧
            pitch (float): 俯仰角
            yaw (float): 偏航角
        """
        height, width = frame.shape[:2]
        
        # 显示头部姿态角度
        cv2.putText(frame, f"Pitch: {pitch:.1f}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"Yaw: {yaw:.1f}", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # 显示状态和持续时间
        if self.pitch_down_start_time is not None:
            cv2.putText(frame, f"Looking down: {self.pitch_down_duration:.1f}s", (10, 90), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        elif self.yaw_left_start_time is not None:
            cv2.putText(frame, f"Turning left: {self.yaw_left_duration:.1f}s", (10, 90), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        elif self.yaw_right_start_time is not None:
            cv2.putText(frame, f"Turning right: {self.yaw_right_duration:.1f}s", (10, 90), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
