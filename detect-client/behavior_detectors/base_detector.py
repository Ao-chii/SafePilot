"""行为检测器基类模块
定义所有行为检测器的基本接口
"""

from abc import ABC, abstractmethod


class BaseDetector(ABC):
    """
    行为检测器基类
    所有具体行为检测器都应继承此类
    """
    
    def __init__(self, config):
        """
        初始化行为检测器
        
        Args:
            config (Config): 配置管理器实例
        """
        self.config = config
        self.behavior_rules = config.get_behavior_rules_config()
    
    @abstractmethod
    def detect(self, yolo_detections, mediapipe_results=None, frame=None):
        """
        检测行为
        
        Args:
            yolo_detections (list): YOLO检测结果
            mediapipe_results (dict): MediaPipe分析结果
            frame: 当前视频帧（可选，用于在视频中显示信息）
            
        Returns:
            list: 检测到的行为事件列表
        """
        pass
    
    def is_instance_of(self, cls):
        """
        检查当前实例是否为指定类的实例
        
        Args:
            cls: 要检查的类
            
        Returns:
            bool: 如果是该类的实例则返回True，否则返回False
        """
        return isinstance(self, cls)