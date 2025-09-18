# 行为分析模块 - 使用策略模式实现各种行为检测

import time
import logging
import numpy as np
import threading
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple, Set

from client.config import config

logger = logging.getLogger("SafePilot.Analyzer")

# 行为类型常量
class BehaviorType:
    """行为类型常量"""
    EYES_CLOSED = "eyes_closed"     # 闭眼
    YAWN = "yawn"                   # 打哈欠
    DISTRACTION = "distraction"     # 分心
    PHONE_USE = "phone_use"         # 使用手机
    SMOKING = "smoking"             # 吸烟
    DRINKING = "drinking"           # 喝水
    DROWSY = "drowsy"               # 疲劳
    NORMAL = "normal"               # 正常状态

# 观察者接口
class BehaviorObserver(ABC):
    """行为观察者接口"""
    
    @abstractmethod
    def on_behavior_detected(self, behavior_type: str, confidence: float, details: Dict[str, Any]) -> None:
        """
        当检测到行为时调用
        
        Args:
            behavior_type: 行为类型
            confidence: 置信度
            details: 详细信息
        """
        pass


# 行为检测策略接口
class BehaviorDetectionStrategy(ABC):
    """行为检测策略接口"""
    
    @abstractmethod
    def detect(self, frame: np.ndarray, detections: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行行为检测
        
        Args:
            frame: 视频帧
            detections: 检测结果，包含YOLO检测和面部关键点
            
        Returns:
            Dict[str, Any]: 包含检测到的行为信息
        """
        pass


# 眼睛状态检测策略
class EyeStateDetectionStrategy(BehaviorDetectionStrategy):
    """眼睛状态检测策略"""
    
    def __init__(self):
        self.config = config.behavior
        self.eye_ar_threshold = self.config["eye_ar_threshold"]
        self.eye_ar_consec_frames = self.config["eye_ar_consec_frames"]
        
        # 状态变量
        self.eye_counter = 0
        self.total_blinks = 0
        self.last_blink_time = time.time()
        self.blink_rate = 0  # 眨眼频率 (次/分钟)
        
        # 状态记录
        self.closed_time = 0
        self.last_frame_time = time.time()
        self.frame_count = 0
    
    def detect(self, frame: np.ndarray, detections: Dict[str, Any]) -> Dict[str, Any]:
        """检测眼睛状态"""
        result = {
            "behavior_type": None,
            "confidence": 0.0,
            "eye_ratio": 0.0,
            "is_closed": False,
            "blink_count": self.total_blinks,
            "blink_rate": self.blink_rate
        }
        
        # 记录帧
        self.frame_count += 1
        current_time = time.time()
        frame_time = current_time - self.last_frame_time
        self.last_frame_time = current_time
        
        # 如果没有面部关键点，无法判断眼睛状态
        if "eye_ratio" not in detections:
            return result
        
        # 获取眼睛长宽比
        eye_ratio = detections["eye_ratio"]
        result["eye_ratio"] = eye_ratio
        
        # 判断眼睛是否闭合
        is_closed = eye_ratio < self.eye_ar_threshold
        result["is_closed"] = is_closed
        
        if is_closed:
            # 增加闭眼计数
            self.eye_counter += 1
            self.closed_time += frame_time
            
            # 判断是否达到闭眼阈值
            if self.eye_counter >= self.eye_ar_consec_frames:
                result["behavior_type"] = BehaviorType.EYES_CLOSED
                
                # 置信度 = 闭眼时间/阈值时间
                threshold_time = self.eye_ar_consec_frames / 30  # 假设30fps
                confidence = min(self.closed_time / threshold_time, 1.0)
                result["confidence"] = confidence
        else:
            # 如果之前的帧是闭眼状态，且达到了阈值，则记录为一次眨眼
            if self.eye_counter >= self.eye_ar_consec_frames:
                self.total_blinks += 1
                result["blink_count"] = self.total_blinks
                
                # 更新眨眼频率
                blink_interval = current_time - self.last_blink_time
                if blink_interval > 0:
                    # 计算每分钟眨眼次数
                    self.blink_rate = 60.0 / blink_interval
                self.last_blink_time = current_time
            
            # 重置计数器和闭眼时间
            self.eye_counter = 0
            self.closed_time = 0
            
            # 正常状态
            result["behavior_type"] = BehaviorType.NORMAL
            result["confidence"] = 1.0
        
        return result


# 嘴巴状态检测策略
class MouthStateDetectionStrategy(BehaviorDetectionStrategy):
    """嘴巴状态检测策略"""
    
    def __init__(self):
        self.config = config.behavior
        self.mouth_ar_threshold = self.config["mouth_ar_threshold"]
        self.mouth_ar_consec_frames = self.config["mouth_ar_consec_frames"]
        
        # 状态变量
        self.mouth_counter = 0
        self.total_yawns = 0
        self.last_yawn_time = time.time()
        self.yawn_rate = 0  # 打哈欠频率 (次/分钟)
        
        # 状态记录
        self.open_time = 0
        self.last_frame_time = time.time()
    
    def detect(self, frame: np.ndarray, detections: Dict[str, Any]) -> Dict[str, Any]:
        """检测嘴巴状态"""
        result = {
            "behavior_type": None,
            "confidence": 0.0,
            "mouth_ratio": 0.0,
            "is_open": False,
            "yawn_count": self.total_yawns,
            "yawn_rate": self.yawn_rate
        }
        
        # 记录帧时间
        current_time = time.time()
        frame_time = current_time - self.last_frame_time
        self.last_frame_time = current_time
        
        # 如果没有面部关键点，无法判断嘴巴状态
        if "mouth_ratio" not in detections:
            return result
        
        # 获取嘴巴长宽比
        mouth_ratio = detections["mouth_ratio"]
        result["mouth_ratio"] = mouth_ratio
        
        # 判断嘴巴是否张开
        is_open = mouth_ratio > self.mouth_ar_threshold
        result["is_open"] = is_open
        
        if is_open:
            # 增加张嘴计数
            self.mouth_counter += 1
            self.open_time += frame_time
            
            # 判断是否达到打哈欠阈值
            if self.mouth_counter >= self.mouth_ar_consec_frames:
                result["behavior_type"] = BehaviorType.YAWN
                
                # 置信度 = 张嘴时间/阈值时间
                threshold_time = self.mouth_ar_consec_frames / 30  # 假设30fps
                confidence = min(self.open_time / threshold_time, 1.0)
                result["confidence"] = confidence
        else:
            # 如果之前的帧是张嘴状态，且达到了阈值，则记录为一次打哈欠
            if self.mouth_counter >= self.mouth_ar_consec_frames:
                self.total_yawns += 1
                result["yawn_count"] = self.total_yawns
                
                # 更新打哈欠频率
                yawn_interval = current_time - self.last_yawn_time
                if yawn_interval > 0:
                    # 计算每小时打哈欠次数
                    self.yawn_rate = 3600.0 / yawn_interval
                self.last_yawn_time = current_time
            
            # 重置计数器和张嘴时间
            self.mouth_counter = 0
            self.open_time = 0
            
            # 正常状态
            result["behavior_type"] = BehaviorType.NORMAL
            result["confidence"] = 1.0
        
        return result


# 分心行为检测策略
class DistractionDetectionStrategy(BehaviorDetectionStrategy):
    """分心行为检测策略"""
    
    def __init__(self):
        self.config = config.behavior
        self.distraction_window = self.config["distraction_window"]
        self.head_pose_threshold = self.config["head_pose_threshold"]
        
        # 检测目标
        self.phone_enabled = self.config["phone_enabled"]
        self.smoke_enabled = self.config["smoke_enabled"]
        self.drink_enabled = self.config["drink_enabled"]
        
        # 状态变量
        self.distraction_counter = 0
        self.distraction_frames = 0
        self.distraction_type = None
        self.distraction_confidence = 0.0
    
    def detect(self, frame: np.ndarray, detections: Dict[str, Any]) -> Dict[str, Any]:
        """检测分心行为"""
        result = {
            "behavior_type": None,
            "confidence": 0.0,
            "distraction_type": None,
            "is_distracted": False
        }
        
        # 分心行为检测
        distraction_detected = False
        distraction_type = None
        distraction_confidence = 0.0
        
        # 检查YOLO检测结果中是否有分心目标
        if "boxes" in detections:
            formatted_boxes = detections.get("formatted_boxes", [])
            
            for box in formatted_boxes:
                label = box.get("label", "").lower()
                confidence = box.get("confidence", 0)
                
                # 检查是否为目标行为
                if (self.phone_enabled and label == "phone" and confidence > 0.5):
                    distraction_detected = True
                    distraction_type = BehaviorType.PHONE_USE
                    distraction_confidence = confidence
                    break
                
                elif (self.smoke_enabled and label == "smoke" and confidence > 0.5):
                    distraction_detected = True
                    distraction_type = BehaviorType.SMOKING
                    distraction_confidence = confidence
                    break
                
                elif (self.drink_enabled and label == "drink" and confidence > 0.5):
                    distraction_detected = True
                    distraction_type = BehaviorType.DRINKING
                    distraction_confidence = confidence
                    break
        
        # 更新分心计数
        if distraction_detected:
            self.distraction_counter += 1
            self.distraction_frames += 1
            self.distraction_type = distraction_type
            self.distraction_confidence = distraction_confidence
            
            # 如果持续检测到分心行为，增加置信度
            if self.distraction_counter >= 3:  # 至少连续3帧检测到
                result["behavior_type"] = distraction_type
                result["confidence"] = min(distraction_confidence * (self.distraction_counter / 5.0), 1.0)
                result["distraction_type"] = distraction_type
                result["is_distracted"] = True
        else:
            # 逐渐减少计数，而不是立即归零，使检测更稳定
            self.distraction_counter = max(0, self.distraction_counter - 1)
            
            if self.distraction_counter >= 3:
                # 仍然保持一定的分心状态，但置信度降低
                result["behavior_type"] = self.distraction_type
                result["confidence"] = self.distraction_confidence * 0.8  # 降低置信度
                result["distraction_type"] = self.distraction_type
                result["is_distracted"] = True
            else:
                # 正常状态
                result["behavior_type"] = BehaviorType.NORMAL
                result["confidence"] = 1.0
                result["is_distracted"] = False
        
        return result


# 疲劳状态检测策略
class FatigueDetectionStrategy(BehaviorDetectionStrategy):
    """疲劳状态检测策略 - PERCLOS模型"""
    
    def __init__(self):
        self.config = config.behavior
        self.perclos_window = self.config["perclos_window"]
        self.perclos_threshold = self.config["perclos_threshold"]
        self.mouth_weight = self.config["mouth_weight"]
        
        # 状态变量
        self.frame_count = 0
        self.closed_eye_frames = 0
        self.yawn_frames = 0
        self.last_perclos = 0.0
    
    def detect(self, frame: np.ndarray, detections: Dict[str, Any]) -> Dict[str, Any]:
        """检测疲劳状态"""
        result = {
            "behavior_type": None,
            "confidence": 0.0,
            "perclos": self.last_perclos,
            "is_fatigued": False,
            "frame_count": self.frame_count,
            "closed_eye_frames": self.closed_eye_frames,
            "yawn_frames": self.yawn_frames
        }
        
        # 增加帧计数
        self.frame_count += 1
        
        # 检查眼睛和嘴巴状态
        if "is_closed" in detections and detections["is_closed"]:
            self.closed_eye_frames += 1
        
        if "is_open" in detections and detections["is_open"]:
            self.yawn_frames += 1
        
        # 当帧数达到窗口大小时，计算PERCLOS值
        if self.frame_count >= self.perclos_window:
            # PERCLOS = 闭眼帧数比例 + 打哈欠帧数比例 * 权重
            perclos = (self.closed_eye_frames / self.frame_count) + \
                     (self.yawn_frames / self.frame_count) * self.mouth_weight
            
            # 更新结果
            result["perclos"] = perclos
            self.last_perclos = perclos
            
            # 判断是否疲劳
            if perclos > self.perclos_threshold:
                result["behavior_type"] = BehaviorType.DROWSY
                
                # 置信度 = PERCLOS值/阈值
                confidence = min(perclos / self.perclos_threshold, 2.0) / 2.0
                result["confidence"] = min(confidence, 1.0)
                result["is_fatigued"] = True
            else:
                result["behavior_type"] = BehaviorType.NORMAL
                result["confidence"] = 1.0
            
            # 重置计数
            self.frame_count = 0
            self.closed_eye_frames = 0
            self.yawn_frames = 0
        
        return result


# 行为分析器 - 观察者模式的主题
class BehaviorAnalyzer:
    """行为分析器类 - 使用策略模式和观察者模式"""
    
    def __init__(self):
        """初始化行为分析器"""
        self.config = config
        
        # 检测策略
        self.strategies = {
            "eye": EyeStateDetectionStrategy(),
            "mouth": MouthStateDetectionStrategy(),
            "distraction": DistractionDetectionStrategy(),
            "fatigue": FatigueDetectionStrategy()
        }
        
        # 观察者列表
        self.observers: List[BehaviorObserver] = []
        
        # 行为状态
        self.current_behaviors: Dict[str, Dict[str, Any]] = {}
        self.detected_behaviors: Set[str] = set()
        
        # 线程锁，保护观察者列表
        self.lock = threading.RLock()
        
        logger.info("BehaviorAnalyzer初始化完成")
    
    def add_observer(self, observer: BehaviorObserver) -> None:
        """添加观察者"""
        with self.lock:
            if observer not in self.observers:
                self.observers.append(observer)
                logger.debug(f"添加观察者: {observer}")
    
    def remove_observer(self, observer: BehaviorObserver) -> None:
        """移除观察者"""
        with self.lock:
            if observer in self.observers:
                self.observers.remove(observer)
                logger.debug(f"移除观察者: {observer}")
    
    def notify_observers(self, behavior_type: str, confidence: float, details: Dict[str, Any]) -> None:
        """通知所有观察者"""
        with self.lock:
            for observer in self.observers:
                try:
                    observer.on_behavior_detected(behavior_type, confidence, details)
                except Exception as e:
                    logger.error(f"通知观察者时出错: {e}")
    
    def analyze(self, frame: np.ndarray, detections: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析行为
        
        Args:
            frame: 视频帧
            detections: 检测结果，包含YOLO和面部关键点
        
        Returns:
            Dict[str, Any]: 行为分析结果
        """
        result = {
            "behaviors": [],
            "details": {},
            "status": {}
        }
        
        try:
            # 确保所有值格式正确
            if "boxes" in detections and isinstance(detections["boxes"], list) and \
               "classes" in detections and isinstance(detections["classes"], list) and \
               "scores" in detections and isinstance(detections["scores"], list):
                
                # 格式化YOLO检测结果
                from client.detector import yolo_detector
                formatted_boxes = yolo_detector.format_results(detections)
                detections["formatted_boxes"] = formatted_boxes
            
            # 运行所有检测策略
            eye_result = self.strategies["eye"].detect(frame, detections)
            mouth_result = self.strategies["mouth"].detect(frame, detections)
            distraction_result = self.strategies["distraction"].detect(frame, detections)
            
            # 更新疲劳检测的输入
            fatigue_input = detections.copy()
            fatigue_input.update(eye_result)
            fatigue_input.update(mouth_result)
            fatigue_result = self.strategies["fatigue"].detect(frame, fatigue_input)
            
            # 收集所有行为
            behaviors = []
            
            # 添加眼睛状态
            if eye_result["behavior_type"] == BehaviorType.EYES_CLOSED:
                behaviors.append({
                    "type": BehaviorType.EYES_CLOSED,
                    "confidence": eye_result["confidence"],
                    "details": {
                        "eye_ratio": eye_result["eye_ratio"],
                        "blink_count": eye_result["blink_count"]
                    }
                })
            
            # 添加嘴巴状态
            if mouth_result["behavior_type"] == BehaviorType.YAWN:
                behaviors.append({
                    "type": BehaviorType.YAWN,
                    "confidence": mouth_result["confidence"],
                    "details": {
                        "mouth_ratio": mouth_result["mouth_ratio"],
                        "yawn_count": mouth_result["yawn_count"]
                    }
                })
            
            # 添加分心状态
            if distraction_result["behavior_type"] not in [None, BehaviorType.NORMAL]:
                behaviors.append({
                    "type": distraction_result["behavior_type"],
                    "confidence": distraction_result["confidence"],
                    "details": {
                        "distraction_type": distraction_result["distraction_type"]
                    }
                })
            
            # 添加疲劳状态
            if fatigue_result["behavior_type"] == BehaviorType.DROWSY:
                behaviors.append({
                    "type": BehaviorType.DROWSY,
                    "confidence": fatigue_result["confidence"],
                    "details": {
                        "perclos": fatigue_result["perclos"],
                        "frame_count": fatigue_result["frame_count"],
                        "closed_eye_frames": fatigue_result["closed_eye_frames"],
                        "yawn_frames": fatigue_result["yawn_frames"]
                    }
                })
            
            # 更新结果
            result["behaviors"] = behaviors
            
            # 合并所有详细信息
            result["details"] = {
                "eye": eye_result,
                "mouth": mouth_result,
                "distraction": distraction_result,
                "fatigue": fatigue_result
            }
            
            # 状态信息，用于显示
            result["status"] = {
                "眼睛比例": f"{eye_result['eye_ratio']:.3f}",
                "嘴巴比例": f"{mouth_result['mouth_ratio']:.3f}",
                "眨眼次数": eye_result["blink_count"],
                "哈欠次数": mouth_result["yawn_count"],
                "PERCLOS": f"{fatigue_result['perclos']:.3f}"
            }
            
            # 通知观察者
            self._notify_all_behaviors(behaviors)
            
        except Exception as e:
            logger.error(f"行为分析错误: {e}")
        
        return result
    
    def _notify_all_behaviors(self, behaviors: List[Dict[str, Any]]) -> None:
        """通知所有检测到的行为"""
        # 获取当前帧中的所有行为类型
        current_behavior_types = set()
        
        for behavior in behaviors:
            behavior_type = behavior["type"]
            confidence = behavior["confidence"]
            details = behavior["details"]
            
            current_behavior_types.add(behavior_type)
            
            # 检查是否是新的行为或者是已经通知过的行为
            is_new_behavior = behavior_type not in self.detected_behaviors
            
            if is_new_behavior:
                # 新检测到的行为，通知观察者
                self.notify_observers(behavior_type, confidence, details)
                self.detected_behaviors.add(behavior_type)
        
        # 检查哪些行为已经停止
        stopped_behaviors = self.detected_behaviors - current_behavior_types
        for behavior_type in stopped_behaviors:
            # 行为已经停止，从集合中移除
            self.detected_behaviors.remove(behavior_type)
    
    def reset(self) -> None:
        """重置所有策略的状态"""
        for strategy in self.strategies.values():
            if hasattr(strategy, "reset") and callable(getattr(strategy, "reset")):
                strategy.reset()
        
        # 清空状态
        self.current_behaviors.clear()
        self.detected_behaviors.clear()


# 创建全局实例
behavior_analyzer = BehaviorAnalyzer()


if __name__ == "__main__":
    # 测试代码
    import cv2
    
    # 测试观察者
    class TestObserver(BehaviorObserver):
        def on_behavior_detected(self, behavior_type, confidence, details):
            print(f"检测到行为: {behavior_type}, 置信度: {confidence:.2f}")
            print(f"详情: {details}")
    
    # 创建分析器
    analyzer = behavior_analyzer
    
    # 添加观察者
    test_observer = TestObserver()
    analyzer.add_observer(test_observer)
    
    # 模拟检测结果
    mock_detections = {
        "eye_ratio": 0.1,  # 闭眼
        "mouth_ratio": 0.7,  # 打哈欠
        "is_closed": True,
        "is_open": True,
        "boxes": [],
        "classes": [],
        "scores": []
    }
    
    # 模拟视频帧
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # 分析行为
    for _ in range(10):  # 模拟10帧
        result = analyzer.analyze(frame, mock_detections)
        print(f"分析结果: {result['behaviors']}")
        time.sleep(0.1)
    
    # 移除观察者
    analyzer.remove_observer(test_observer)
    print("测试完成")
