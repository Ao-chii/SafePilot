"""双手脱离方向盘检测器模块
负责检测驾驶员双手脱离方向盘的行为
"""

import time
from events import EventLevel, DangerousBehavior, BehaviorEvent
from .base_detector import BaseDetector


class HandsOffWheelDetector(BaseDetector):
    """
    双手脱离方向盘检测器类
    检测驾驶员双手脱离方向盘的行为
    """
    
    def __init__(self, config):
        """
        初始化双手脱离方向盘检测器
        
        Args:
            config (Config): 配置管理器实例
        """
        super().__init__(config)
        self.hands_last_seen_on_wheel = time.time()
        # 方向盘区域（图像底部中央区域）
        # 这些值需要根据实际摄像头安装位置进行调整
        self.wheel_region = None
    
    def detect(self, yolo_detections, mediapipe_results, frame=None):
        """
        检测双手脱离方向盘行为
        
        Args:
            yolo_detections (list): YOLO检测结果
            mediapipe_results (dict): MediaPipe分析结果
            frame: 当前视频帧（可选，用于在视频中显示信息）
            
        Returns:
            list: 检测到的行为事件列表
        """
        events = []
        
        # 更新方向盘区域（根据当前帧尺寸）
        if frame is not None and self.wheel_region is None:
            self._update_wheel_region(frame)
            
        self._detect_hands_off_wheel(events, mediapipe_results)
        return events
    
    def _update_wheel_region(self, frame):
        """
        更新方向盘区域坐标
        
        Args:
            frame: 视频帧
        """
        height, width = frame.shape[:2]
        # 定义方向盘区域为图像底部中央区域
        self.wheel_region = {
            'x_min': width // 4,
            'x_max': 3 * width // 4,
            'y_min': 2 * height // 3,
            'y_max': height
        }
    
    def _detect_hands_off_wheel(self, events, mediapipe_results):
        """
        检测双手脱离方向盘行为
        
        Args:
            events (list): 事件列表
            mediapipe_results (dict): MediaPipe分析结果
        """
        # 检查手部关键点是否在方向盘区域内
        hands_on_wheel = self._check_hands_in_wheel_region(mediapipe_results)
        
        if not hands_on_wheel:
            # 计算双手脱离方向盘的时间
            time_off = time.time() - self.hands_last_seen_on_wheel
            hands_off_wheel_threshold = self.behavior_rules.get('hands_off_wheel_threshold', 3.0)
            
            if time_off > hands_off_wheel_threshold:
                # 双手脱离方向盘超过阈值时间
                event = BehaviorEvent(
                    event_type=EventLevel.DANGER,
                    behavior=DangerousBehavior.HANDS_OFF_WHEEL,
                    confidence=min(0.5 + (time_off / 10.0), 1.0),  # 置信度随时间增加
                    timestamp=time.time(),
                    details={
                        'time_off_wheel': time_off
                    }
                )
                events.append(event)
        else:
            # 更新最后检测到手在方向盘上的时间
            self.hands_last_seen_on_wheel = time.time()
    
    def _check_hands_in_wheel_region(self, mediapipe_results):
        """
        检查手部关键点是否在方向盘区域内
        
        Args:
            mediapipe_results (dict): MediaPipe分析结果
            
        Returns:
            bool: 手是否在方向盘区域
        """
        if not mediapipe_results['hands'].multi_hand_landmarks or not self.wheel_region:
            return False
        
        # 检查是否有任何手部关键点在方向盘区域内
        for hand_landmarks in mediapipe_results['hands'].multi_hand_landmarks:
            for landmark in hand_landmarks.landmark:
                x_pixel = landmark.x * self.wheel_region['x_max'] * 2  # 粗略转换
                y_pixel = landmark.y * self.wheel_region['y_max'] * 2  # 粗略转换
                
                if (self.wheel_region['x_min'] <= x_pixel <= self.wheel_region['x_max'] and
                    self.wheel_region['y_min'] <= y_pixel <= self.wheel_region['y_max']):
                    return True
        
        return False