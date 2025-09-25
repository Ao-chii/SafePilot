"""
行为事件定义模块
定义系统中使用的行为事件类型和枚举
"""

from enum import Enum
import time
import numpy as np


class EventLevel(Enum):
    """
    事件类型枚举
    """
    DANGER = "DANGER"      # 危险事件
    WARNING = "WARNING"    # 警告事件


class DangerousBehavior(Enum):
    """
    危险行为枚举
    """
    PHONE_CALL = 1           # 手机通话
    PHONE_READING = 2        # 看手机
    HANDS_OFF_WHEEL = 3      # 双手脱离方向盘
    SEVERE_DROWSINESS = 4    # 严重疲劳驾驶
    GAZE_OFF_ROAD = 5        # 视线偏离道路
    SMOKING = 6              # 抽烟
    TURNING_AROUND = 7       # 转身与后排乘客交流


class WarningBehavior(Enum):
    """
    警告行为枚举
    """
    EATING_DRINKING = 1      # 饮食/喝水
    INFOTAINMENT_SYSTEM = 2  # 操作车载信息娱乐系统
    ADJUSTING_EQUIPMENT = 3  # 过度调整车内设备
    EXCESSIVE_TALKING = 4    # 与乘客过度交谈
    MILD_DROWSINESS = 5      # 轻度疲劳迹象
    ABNORMAL_HEAD_POSE = 6   # 异常头部姿势
    NO_SEATBELT = 7          # 未佩戴安全带
    DRIVER_NOT_PRESENT = 8   # 驾驶员不存在

class EventTypeToString:
    """
    事件类型到字符串的映射
    """
    event_map={
        DangerousBehavior.PHONE_READING:"使用手机",
        DangerousBehavior.SEVERE_DROWSINESS:"疲劳驾驶"
    }
    def get_event_type_string(self,event_type):
        return self.event_map.get(event_type, "未知行为")
 



class BehaviorEvent:
    """
    行为事件类
    表示检测到的一个行为事件
    """
    
    def __init__(self, event_type,confidence, timestamp=None, driver_id=1, details=None):
        """
        初始化行为事件
        
        Args:
            event_type (EventType): 事件类型
            behavior (Enum): 具体行为（DangerousBehavior或WarningBehavior）
            confidence (float): 置信度
            timestamp (float): 时间戳
            driver_id (int): 司机ID
            details (dict): 事件详情
        """
        self.type = event_type
        self.confidence = confidence
        self.timestamp = timestamp if timestamp is not None else time.time()
        self.driver_id = driver_id
        self.details = details if details is not None else {}
    
    def __str__(self):
        """
        返回事件的字符串表示
        """
        return f"[{self.type.name}] (Confidence: {self.confidence:.2f})"
    
    def to_dict(self):
        """
        将事件转换为字典格式
        
        Returns:
            dict: 事件字典
        """
        # 处理details中的numpy数组或其他不可序列化对象
        def convert_to_serializable(obj):
            if isinstance(obj, (list, tuple)):
                return [convert_to_serializable(item) for item in obj]
            elif isinstance(obj, dict):
                return {key: convert_to_serializable(value) for key, value in obj.items()}
            elif hasattr(obj, 'item'):  # numpy标量
                return obj.item()
            elif isinstance(obj, (int, float, str, bool)) or obj is None:
                return obj
            else:
                return str(obj)  # 其他对象转换为字符串
        
        details_serializable = convert_to_serializable(self.details)
        
        return {
            "driver_id": self.driver_id,
            "confidence": self.confidence,
            "timestamp": self.timestamp,
            "details": details_serializable
        }