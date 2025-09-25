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
    检测驾驶员使用手机的行为
    """
    
    def __init__(self, config):
        """
        初始化手机使用检测器
        
        Args:
            config (Config): 配置管理器实例
        """
        super().__init__(config)
        self.phone_detected_time = None
    
    def detect(self, yolo_detections, mediapipe_results, frame=None):
        """
        检测手机使用行为
        
        Args:
            yolo_detections (list): YOLO检测结果
            mediapipe_results (dict): MediaPipe分析结果
            frame: 当前视频帧（可选，用于在视频中显示信息）
            
        Returns:
            list: 检测到的行为事件列表
        """
        events = []
        self._detect_phone_usage(events, yolo_detections, mediapipe_results, frame)
        return events
    
    def _detect_phone_usage(self, events, yolo_detections, mediapipe_results, frame=None):
        """
        检测手机使用行为
        
        Args:
            events (list): 事件列表
            yolo_detections (list): YOLO检测结果
            mediapipe_results (dict): MediaPipe分析结果
            frame: 视频帧（可选，用于显示检测信息）
        """
        # 检查是否检测到手机
        phone_detections = [det for det in yolo_detections if det['class_name'] == 'cell phone']
        
        if not phone_detections:
            return
            
        # 获取置信度最高的手机检测结果
        phone_detection = max(phone_detections, key=lambda x: x['confidence'])
        phone_confidence = phone_detection['confidence']
        phone_bbox = phone_detection['bbox']  # [x1, y1, x2, y2]
        
        # 检查是否有手部关键点
        hand_landmarks = mediapipe_results['hands'].multi_hand_landmarks
        face_landmarks = mediapipe_results['face'].multi_face_landmarks
        
        # 计算手机位置
        phone_center_x = (phone_bbox[0] + phone_bbox[2]) / 2
        phone_center_y = (phone_bbox[1] + phone_bbox[3]) / 2
        
        # 检查手是否在手机附近
        hands_near_phone = False
        if hand_landmarks:
            for hand_landmark in hand_landmarks:
                # 检查手部关键点是否在手机附近
                for landmark in hand_landmark.landmark:
                    # 将归一化坐标转换为像素坐标
                    if frame is not None:
                        height, width = frame.shape[:2]
                        x_pixel = int(landmark.x * width)
                        y_pixel = int(landmark.y * height)
                        
                        # 计算手部关键点与手机中心的距离
                        distance = np.sqrt((x_pixel - phone_center_x)**2 + (y_pixel - phone_center_y)**2)
                        
                        # 如果距离小于阈值，则认为手在手机附近
                        # 阈值根据手机框的大小动态调整
                        phone_width = phone_bbox[2] - phone_bbox[0]
                        if distance < phone_width:
                            hands_near_phone = True
                            break
                if hands_near_phone:
                    break
        
        # 检查驾驶员面部朝向（如果检测到面部）
        face_looking_down = False
        if face_landmarks:
            face_landmark = face_landmarks[0]
            # 简单判断：如果鼻子的y坐标大于手机中心y坐标，可能在看手机
            nose_landmark = face_landmark.landmark[1]  # 鼻子关键点索引为1
            if frame is not None:
                height, width = frame.shape[:2]
                nose_y = nose_landmark.y * height
                # 如果鼻子位置低于手机中心位置，可能在看手机
                if nose_y > phone_center_y:
                    face_looking_down = True
        
        # 综合判断是否在使用手机
        # 条件：检测到手机 + (手在手机附近 或 面部朝下看手机)
        phone_usage_detected = phone_confidence > 0.5 and (hands_near_phone or face_looking_down)
        
        # 在视频画面中显示手机检测框和相关信息
        if frame is not None:
            # 绘制手机检测框
            x1, y1, x2, y2 = phone_bbox
            color = (0, 0, 255) if phone_usage_detected else (0, 255, 0)  # 红色表示检测到使用，绿色表示仅检测到手机
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            # 显示手机使用信息
            if phone_usage_detected:
                cv2.putText(frame, "PHONE USAGE DETECTED", (x1, y1 - 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                cv2.putText(frame, f"Confidence: {phone_confidence:.2f}", (x1, y1 - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
            else:
                cv2.putText(frame, "PHONE DETECTED", (x1, y1 - 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"Confidence: {phone_confidence:.2f}", (x1, y1 - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        # 如果检测到手机使用行为，则添加事件
        if phone_usage_detected:
            # 计算综合置信度
            # 综合考虑YOLO检测置信度、手部接近程度和面部朝向
            hand_factor = 1.0 if hands_near_phone else 0.7
            face_factor = 1.0 if face_looking_down else 0.8
            overall_confidence = phone_confidence * hand_factor * face_factor
            
            event = BehaviorEvent(
                event_type=DangerousBehavior.PHONE_READING,
                confidence=round(overall_confidence,2),
                timestamp=time.time(),
                details={
                    'phone_confidence': round(float(phone_confidence),2),
                    'hands_near_phone': hands_near_phone,
                    'face_looking_down': face_looking_down
                }
            )
            events.append(event)