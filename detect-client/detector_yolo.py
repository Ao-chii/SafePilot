"""
YOLO检测模块
封装YOLO模型，负责检测驾驶员和危险物品
"""

import cv2
import numpy as np
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("警告: 未安装ultralytics库，YOLO检测功能不可用")


class YOLODetector:
    """
    YOLO检测器类
    负责使用YOLO模型检测视频帧中的对象
    """
    
    def __init__(self, model_path, conf_threshold=0.5, classes=None):
        """
        初始化YOLO检测器
        
        Args:
            model_path (str): YOLO模型文件路径
            conf_threshold (float): 置信度阈值
            classes (list): 需要检测的类别ID列表，None表示检测所有类别
        """
        if not YOLO_AVAILABLE:
            raise RuntimeError("YOLO功能不可用，请安装ultralytics库: pip install ultralytics")
        
        self.model = YOLO(model_path)
        self.conf_threshold = conf_threshold
        self.classes = classes
    
    def detect(self, frame):
        """
        检测视频帧中的对象
        
        Args:
            frame: 输入视频帧
            
        Returns:
            tuple: (检测结果列表, 绘制了检测框的图像)
        """
        # 使用YOLO模型检测
        results = self.model(frame, verbose=False, conf=self.conf_threshold, classes=self.classes)
        
        # 处理检测结果
        result = results[0] if len(results) > 0 else None
        detections = []
        
        if result and result.boxes is not None:
            for box in result.boxes:
                # 提取边界框坐标
                xyxy = box.xyxy[0].cpu().numpy().astype(int)  # 边框坐标 [x1, y1, x2, y2]
                conf = box.conf[0].cpu().numpy()              # 置信度
                cls_id = int(box.cls[0].cpu().numpy())        # 类别ID
                
                detections.append({
                    'class_id': cls_id,
                    'class_name': result.names[cls_id],
                    'confidence': conf,
                    'bbox': xyxy
                })
        
        # 返回检测结果和绘制了检测框的图像
        return detections, result.plot() if result else frame