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
    通过检测手部关键点与嘴部位置的关系来判断是否在喝水
    """
    
    def __init__(self, config):
        """
        初始化喝水检测器
        
        Args:
            config (Config): 配置管理器实例
        """
        super().__init__(config)
        # 手部关键点索引
        self.WRIST = 0  # 手腕
        self.THUMB_TIP = 4  # 拇指尖
        self.INDEX_FINGER_TIP = 8  # 食指尖
        self.MIDDLE_FINGER_TIP = 12  # 中指尖
        self.RING_FINGER_TIP = 16  # 无名指尖
        self.PINKY_TIP = 20  # 小指尖
        
        # 嘴部关键点索引
        self.MOUTH_LEFT = 61   # 嘴巴左边
        self.MOUTH_RIGHT = 291  # 嘴巴右边
        self.MOUTH_TOP = 0      # 嘴巴上边
        self.MOUTH_BOTTOM = 17  # 嘴巴下边
        
        # 用于状态跟踪的变量
        self.drinking_deque = []  # 记录最近的喝水检测状态
        self.last_drinking_time = time.time()
    
    def detect(self, yolo_detections, mediapipe_results, frame=None):
        """
        检测喝水行为
        
        Args:
            yolo_detections (list): YOLO检测结果
            mediapipe_results (dict): MediaPipe分析结果
            frame: 当前视频帧（可选，用于在视频中显示信息）
            
        Returns:
            list: 检测到的行为事件列表
        """
        events = []
        self._detect_drinking(events, yolo_detections, mediapipe_results, frame)
        return events
    
    def _detect_drinking(self, events, yolo_detections, mediapipe_results, frame=None):
        """
        检测喝水行为
        
        Args:
            events (list): 事件列表
            yolo_detections (list): YOLO检测结果
            mediapipe_results (dict): MediaPipe分析结果
            frame: 视频帧（可选，用于显示检测信息）
        """
        # 检查是否检测到水杯
        bottle_detections = [det for det in yolo_detections if det['class_id'] == 39 or det['class_id']==41]  # bottle类别ID
        
        if not bottle_detections:
            return  # 如果没有检测到水杯，则不进行喝水检测
        
        # 获取置信度最高的水杯检测结果
        bottle_detection = max(bottle_detections, key=lambda x: x['confidence'])
        bottle_confidence = bottle_detection['confidence']
        bottle_bbox = bottle_detection['bbox']  # [x1, y1, x2, y2]
        
        # 检查是否检测到手部和面部
        hand_landmarks = mediapipe_results['hands'].multi_hand_landmarks
        face_landmarks = mediapipe_results['face'].multi_face_landmarks
        
        if not hand_landmarks or not face_landmarks:
            return
        
        # 获取面部关键点
        face_landmark = face_landmarks[0]
        
        # 计算嘴部中心点
        mouth_left = face_landmark.landmark[self.MOUTH_LEFT]
        mouth_right = face_landmark.landmark[self.MOUTH_RIGHT]
        mouth_top = face_landmark.landmark[self.MOUTH_TOP]
        mouth_bottom = face_landmark.landmark[self.MOUTH_BOTTOM]
        
        mouth_center_x = (mouth_left.x + mouth_right.x) / 2
        mouth_center_y = (mouth_top.y + mouth_bottom.y) / 2
        
        if frame is not None:
            height, width = frame.shape[:2]
            mouth_center_px = (int(mouth_center_x * width), int(mouth_center_y * height))
            
            # 在视频画面中绘制嘴部中心点
            cv2.circle(frame, mouth_center_px, 5, (0, 255, 255), -1)  # 青色点表示嘴部中心
        
        # 检查是否有手靠近嘴部或者手握水杯
        hands_near_mouth = False
        min_distance = float('inf')
        bottle_in_hand = False
        
        # 检查每只手是否靠近嘴部
        for hand_landmark in hand_landmarks:
            # 获取手部关键点坐标
            wrist = hand_landmark.landmark[self.WRIST]
            thumb_tip = hand_landmark.landmark[self.THUMB_TIP]
            index_finger_tip = hand_landmark.landmark[self.INDEX_FINGER_TIP]
            
            # 计算手指尖到嘴部中心的距离
            if frame is not None:
                height, width = frame.shape[:2]
                
                # 转换为像素坐标
                wrist_px = (int(wrist.x * width), int(wrist.y * height))
                thumb_tip_px = (int(thumb_tip.x * width), int(thumb_tip.y * height))
                index_finger_tip_px = (int(index_finger_tip.x * width), int(index_finger_tip.y * height))
                mouth_center_px = (int(mouth_center_x * width), int(mouth_center_y * height))
                
                # 计算距离
                distance_thumb = np.sqrt((thumb_tip_px[0] - mouth_center_px[0])**2 + 
                                        (thumb_tip_px[1] - mouth_center_px[1])**2)
                distance_index = np.sqrt((index_finger_tip_px[0] - mouth_center_px[0])**2 + 
                                        (index_finger_tip_px[1] - mouth_center_px[1])**2)
                distance_wrist = np.sqrt((wrist_px[0] - mouth_center_px[0])**2 + 
                                       (wrist_px[1] - mouth_center_px[1])**2)
                
                # 更新最小距离
                min_distance = min(min_distance, distance_thumb, distance_index, distance_wrist)
                
                # 绘制手部关键点
                cv2.circle(frame, thumb_tip_px, 5, (255, 0, 0), -1)  # 蓝色点表示拇指
                cv2.circle(frame, index_finger_tip_px, 5, (0, 255, 0), -1)  # 绿色点表示食指
                cv2.circle(frame, wrist_px, 5, (0, 0, 255), -1)  # 红色点表示手腕
                
                # 如果距离小于阈值，则认为手在嘴部附近
                # 阈值根据帧的尺寸动态调整
                if frame is not None:
                    threshold = min(height, width) * 0.15  # 增加阈值到15%的最小边长
                    if (distance_thumb < threshold or 
                        distance_index < threshold or 
                        distance_wrist < threshold):
                        hands_near_mouth = True
            
            # 检查手是否握着水杯（手腕在水杯边界框内）
            if frame is not None:
                height, width = frame.shape[:2]
                wrist_x = int(wrist.x * width)
                wrist_y = int(wrist.y * height)
                
                x1, y1, x2, y2 = bottle_bbox
                if x1 <= wrist_x <= x2 and y1 <= wrist_y <= y2:
                    bottle_in_hand = True
        
        # 判断是否在喝水
        # 条件：检测到水杯 + (手在嘴部附近 或者 手握水杯)
        drinking_detected = False
        if frame is not None:
            threshold = min(frame.shape[0], frame.shape[1]) * 0.15  # 使用相同的阈值
            if min_distance < threshold or bottle_in_hand:
                drinking_detected = True
        
        # 在视频画面中显示喝水检测信息
        if frame is not None:
            # 绘制水杯检测框
            x1, y1, x2, y2 = bottle_bbox
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 0), 2)  # 青色框表示水杯
            
            # 显示是否检测到手握水杯
            cv2.putText(frame, f"Bottle in hand: {bottle_in_hand}", (10, 150), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1)
            
            if drinking_detected:
                cv2.putText(frame, "DRINKING DETECTED", (10, 120), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                cv2.putText(frame, f"Min distance: {min_distance:.1f}", (10, 90), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                # cv2.putText(frame, f"Bottle Confidence: {bottle_confidence:.2f}", (10, 120), 
                #            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
        
        # 如果检测到喝水行为，则添加事件
        if drinking_detected:
            # 计算综合置信度（水杯置信度和手部接近程度的综合）
            hand_confidence = max(0.5, 1.0 - (min_distance / (frame.shape[0] if frame is not None else 640)))
            overall_confidence = (bottle_confidence + hand_confidence) / 2
            overall_confidence = round(min(overall_confidence, 1.0), 2)
            
            # 如果是手握水杯的情况，增加置信度
            if bottle_in_hand:
                overall_confidence = min(1.0, overall_confidence + 0.2)
                overall_confidence = round(overall_confidence, 2)
            
            event = BehaviorEvent(
                event_type=WarningBehavior.EATING_DRINKING,
                confidence=overall_confidence,
                timestamp=time.time(),
                details={
                    'min_distance': round(float(min_distance), 1) if frame is not None else 0,
                    'bottle_confidence': round(float(bottle_confidence), 2),
                    'hands_near_mouth': hands_near_mouth,
                    'bottle_in_hand': bottle_in_hand
                }
            )
            events.append(event)
    
    def _draw_hand_landmarks(self, frame, hand_landmarks):
        """
        在视频帧上绘制手部关键点，便于测试和调试
        
        Args:
            frame: 视频帧
            hand_landmarks: 手部关键点
        """
        height, width = frame.shape[:2]
        
        # 绘制手部关键点
        for idx, landmark in enumerate(hand_landmarks.landmark):
            x = int(landmark.x * width)
            y = int(landmark.y * height)
            cv2.circle(frame, (x, y), 3, (0, 0, 255), -1)  # 红色点表示手部关键点