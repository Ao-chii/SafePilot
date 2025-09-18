# YOLOv11检测的接口函数
# 使用Ultralytics库进行目标检测

import numpy as np
import cv2
from ultralytics import YOLO
from numpy import random
import os
from config import get_yolo_config

class YOLODetector:
    """YOLOv11检测器类"""
    
    def __init__(self, config=None):
        """
        初始化YOLOv11检测器
        
        Args:
            config: YOLOConfig配置对象，如果为None则使用默认配置
        """
        # 获取配置
        if config is None:
            config = get_yolo_config()
        
        self.config = config
        self.model_path = config.model_path
        self.device = config.device
        self.conf_thres = config.conf_thres
        self.iou_thres = config.iou_thres
        self.imgsz = config.imgsz
        
        # 检查模型文件是否存在
        actual_model_path = self.model_path
        if not os.path.exists(self.model_path):
            print(f"警告: 权重文件 {self.model_path} 不存在，将使用预训练模型 {config.fallback_model}")
            actual_model_path = config.fallback_model
        
        # 加载模型
        print(f"正在加载YOLOv11模型: {actual_model_path}")
        try:
            self.model = YOLO(actual_model_path)
            print(f"✓ 成功加载模型: {actual_model_path}")
        except Exception as e:
            print(f"模型加载失败: {e}")
            print(f"尝试使用最小模型: yolo11n.pt")
            self.model = YOLO('yolo11n.pt')
        
        # 获取类别名称和颜色
        self.names = self.model.names
        self.colors = [[random.randint(0, 255) for _ in range(3)] for _ in self.names]
        
        # 模型预热
        if config.enable_warmup:
            print("正在进行模型预热...")
            dummy_img = np.zeros((self.imgsz, self.imgsz, 3), dtype=np.uint8)
            self.model(dummy_img, verbose=config.verbose)
            print("✓ 模型预热完成")
        
        print("✓ YOLOv11检测器初始化完成")

# 全局检测器实例
detector = None

def initialize_detector():
    """初始化全局检测器"""
    global detector
    if detector is None:
        print("=== 初始化YOLOv11检测器 ===")
        config = get_yolo_config()
        
        # 验证配置
        errors = config.validate_config()
        if errors:
            print("配置验证失败:")
            for error in errors:
                print(f"  - {error}")
            print("使用默认配置继续...")
        
        detector = YOLODetector(config)
        print("=== 检测器初始化完成 ===")
    return detector

# 在模块导入时初始化检测器
detector = initialize_detector()
 
 
def predict(im0s):
    """
    使用YOLOv11进行目标检测预测
    
    Args:
        im0s: 输入图像 (BGR格式的numpy数组)
    
    Returns:
        ret: 检测结果列表，每个元素为[label, prob, xyxy]
            - label: 标签信息 'face', 'smoke', 'drink', 'phone' 等
            - prob: 对应的置信度 (百分比)
            - xyxy: 对应的位置信息（外框坐标列表 [x1, y1, x2, y2]）
    """
    global detector
    
    if detector is None:
        detector = initialize_detector()
    
    try:
        # 使用YOLOv11进行推理
        results = detector.model(
            im0s, 
            conf=detector.conf_thres, 
            iou=detector.iou_thres,
            imgsz=detector.imgsz,
            verbose=False
        )
        
        # 处理检测结果
        ret = []
        if len(results) > 0:
            result = results[0]  # 取第一个结果（单张图像）
            
            # 检查是否有检测框
            if result.boxes is not None and len(result.boxes) > 0:
                boxes = result.boxes
                
                # 遍历每个检测框
                for i in range(len(boxes)):
                    # 获取边界框坐标
                    xyxy = boxes.xyxy[i].cpu().numpy().astype(int)
                    
                    # 获取置信度
                    conf = float(boxes.conf[i].cpu().numpy())
                    
                    # 获取类别
                    cls = int(boxes.cls[i].cpu().numpy())
                    
                    # 获取类别名称
                    if cls < len(detector.names):
                        label = detector.names[cls]
                    else:
                        label = f'class_{cls}'
                    
                    # 转换置信度为百分比
                    prob = round(conf * 100, 2)
                    
                    # 转换xyxy为列表格式以保持兼容性
                    xyxy_list = [int(xyxy[0]), int(xyxy[1]), int(xyxy[2]), int(xyxy[3])]
                    
                    # 添加到结果列表
                    ret_i = [label, prob, xyxy_list]
                    ret.append(ret_i)
        
        return ret
        
    except Exception as e:
        print(f"检测过程中出现错误: {e}")
        return []


def update_detection_params(conf_thres=None, iou_thres=None):
    """
    动态更新检测参数
    
    Args:
        conf_thres: 新的置信度阈值
        iou_thres: 新的IoU阈值
    """
    global detector
    if detector is not None:
        if conf_thres is not None:
            detector.conf_thres = conf_thres
            detector.config.conf_thres = conf_thres
            print(f"✓ 置信度阈值已更新为: {conf_thres}")
        
        if iou_thres is not None:
            detector.iou_thres = iou_thres
            detector.config.iou_thres = iou_thres
            print(f"✓ IoU阈值已更新为: {iou_thres}")


def get_detector_info():
    """获取检测器信息"""
    global detector
    if detector is None:
        return {"status": "未初始化"}
    
    return {
        "status": "已初始化",
        "model_path": detector.model_path,
        "device": detector.device,
        "conf_thres": detector.conf_thres,
        "iou_thres": detector.iou_thres,
        "imgsz": detector.imgsz,
        "class_names": list(detector.names.values()) if detector.names else [],
        "class_count": len(detector.names) if detector.names else 0
    }


def reset_detector():
    """重置检测器（重新初始化）"""
    global detector
    detector = None
    return initialize_detector()


# 添加一些便利的检测函数
def quick_detect(image_path):
    """
    快速检测单张图片
    
    Args:
        image_path: 图片路径
    
    Returns:
        检测结果列表
    """
    import cv2
    
    # 读取图像
    image = cv2.imread(image_path)
    if image is None:
        print(f"无法读取图像: {image_path}")
        return []
    
    # 进行检测
    return predict(image)