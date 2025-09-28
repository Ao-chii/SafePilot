"""行为判断引擎模块
这是系统的核心逻辑，负责根据YOLO和MediaPipe的结果判断驾驶员行为
"""

from config import Config
from behavior_detectors import DrowsinessDetector, PhoneUsageDetector, HandsOffWheelDetector, YawningDetector, DrinkingDetector


class BehaviorEngine:
    """
    行为判断引擎类
    负责根据检测结果判断驾驶员行为
    """
    
    def __init__(self, config):
        """
        初始化行为判断引擎
        
        Args:
            config (Config): 配置管理器实例
        """
        self.config = config
        
        # 初始化各种行为检测器
        self.detectors = [
            DrowsinessDetector(config),
            PhoneUsageDetector(config),
            # HandsOffWheelDetector(config),
            YawningDetector(config),
            DrinkingDetector(config)
        ]
    
    def process(self, yolo_detections, self_yolo_detections, mediapipe_results, frame, self_frame):
        """
        主处理函数，返回检测到的事件列表
        
        Args:
            yolo_detections (list): YOLO检测结果
            self_yolo_detections (list): 自己训练的YOLO模型检测结果
            mediapipe_results (dict): MediaPipe分析结果
            frame: 当前视频帧
            self_frame: 自己训练的YOLO模型标注后的视频帧
            
        Returns:
            list: 检测到的行为事件列表
        """
        all_events = []
        
        # 使用各个检测器检测行为
        for detector in self.detectors:
            if detector.is_instance_of(PhoneUsageDetector):
                events = detector.detect(self_yolo_detections, self_frame)
            elif detector.is_instance_of(DrinkingDetector):
                events = detector.detect(self_yolo_detections, self_frame)
            else:
                events = detector.detect(yolo_detections, mediapipe_results, frame)

            if events:
                all_events.extend(events)
        
        return all_events