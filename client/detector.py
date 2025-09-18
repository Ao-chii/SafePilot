# 检测模块 - YOLO检测器

import os
import time
import logging
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Union, Tuple, Optional

from client.config import config, WEIGHTS_DIR

logger = logging.getLogger("SafePilot.Detector")

class YOLODetector:
    """YOLOv11检测器类 - 单例模式"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(YOLODetector, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self.config = config
        
        # 模型参数
        self.model_path = self.config.model["yolo_model"]
        self.fallback_model = self.config.model["fallback_model"]
        self.device = self.config.model["device"]
        self.conf_threshold = self.config.model["conf_threshold"]
        self.iou_threshold = self.config.model["iou_threshold"]
        self.img_size = self.config.model["img_size"]
        
        # 模型和类别
        self.model = None
        self.class_names = []
        self.colors = {}
        
        # 加载模型
        self._load_model()
        
        logger.info(f"YOLODetector初始化完成, 使用模型: {self.model_path}")
    
    def _load_model(self):
        """加载YOLOv11模型"""
        try:
            # 检查模型文件是否存在
            if not os.path.exists(self.model_path):
                logger.warning(f"模型文件不存在: {self.model_path}, 尝试使用备用模型")
                self.model_path = self.fallback_model
            
            # 导入YOLO库 (延迟导入以减少启动时间)
            from ultralytics import YOLO
            
            # 加载模型
            logger.info(f"正在加载YOLO模型: {self.model_path}")
            self.model = YOLO(self.model_path)
            
            # 获取类别名称
            self.class_names = self.model.names
            
            # 为每个类别生成颜色
            import random
            for class_id, class_name in self.class_names.items():
                self.colors[class_id] = [random.randint(0, 255) for _ in range(3)]
            
            # 预热模型
            logger.info("模型预热中...")
            dummy_img = np.zeros((640, 640, 3), dtype=np.uint8)
            _ = self.model(dummy_img, verbose=False)
            
            logger.info(f"YOLO模型加载成功，检测类别: {len(self.class_names)}")
        
        except ImportError:
            logger.error("无法导入ultralytics库，请安装: pip install ultralytics>=8.0.0")
            raise
        
        except Exception as e:
            logger.error(f"加载YOLO模型失败: {e}")
            raise
    
    def detect(self, frame: np.ndarray) -> Dict[str, Any]:
        """
        执行目标检测
        
        Args:
            frame: 输入图像
            
        Returns:
            Dict: 检测结果，包含boxes, classes, scores等
        """
        if self.model is None:
            logger.error("模型未加载")
            return {"boxes": [], "classes": [], "scores": []}
        
        try:
            # 执行模型推理
            results = self.model(
                frame,
                conf=self.conf_threshold,
                iou=self.iou_threshold,
                imgsz=self.img_size,
                verbose=False
            )
            
            # 解析结果
            boxes = []
            classes = []
            scores = []
            
            if len(results) > 0 and results[0].boxes is not None:
                result = results[0]  # 第一个批次
                
                # 提取边界框信息
                if hasattr(result.boxes, 'xyxy') and len(result.boxes.xyxy) > 0:
                    for i in range(len(result.boxes)):
                        # 边界框坐标
                        box = result.boxes.xyxy[i].cpu().numpy()
                        
                        # 类别ID和置信度
                        cls_id = int(result.boxes.cls[i].item())
                        conf = float(result.boxes.conf[i].item())
                        
                        # 类别名称
                        if cls_id in self.class_names:
                            cls_name = self.class_names[cls_id]
                        else:
                            cls_name = f"class_{cls_id}"
                        
                        # 添加到结果列表
                        boxes.append(box.tolist())
                        classes.append(cls_name)
                        scores.append(conf)
            
            # 返回结果
            return {
                "boxes": boxes,       # 边界框坐标 [[x1,y1,x2,y2], ...]
                "classes": classes,   # 类别名称 ["person", "car", ...]
                "scores": scores      # 置信度 [0.98, 0.86, ...]
            }
        
        except Exception as e:
            logger.error(f"检测过程中出错: {e}")
            return {"boxes": [], "classes": [], "scores": []}
    
    def format_results(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """将检测结果格式化为标准格式"""
        formatted = []
        
        for i, (box, cls_name, score) in enumerate(zip(
            results["boxes"], results["classes"], results["scores"])):
            
            # 确保box是列表
            if not isinstance(box, list):
                box = box.tolist() if hasattr(box, "tolist") else list(box)
            
            # 确保坐标是整数
            x1, y1, x2, y2 = [int(coord) for coord in box]
            
            formatted.append({
                "id": i,
                "label": cls_name,
                "confidence": float(score),
                "xyxy": [x1, y1, x2, y2]
            })
        
        return formatted


class FaceDetector:
    """面部检测器类 - 使用MediaPipe FaceMesh进行面部关键点检测"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FaceDetector, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self.config = config
        self.use_mediapipe = self.config.model["facemesh_model"]
        self.face_mesh = None
        
        # 如果启用了MediaPipe，则初始化模型
        if self.use_mediapipe:
            self._initialize_mediapipe()
        
        logger.info(f"FaceDetector初始化完成，使用MediaPipe: {self.use_mediapipe}")
    
    def _initialize_mediapipe(self):
        """初始化MediaPipe模型"""
        try:
            import mediapipe as mp
            
            # 初始化面部网格检测器
            self.mp = mp
            self.face_mesh = mp.solutions.face_mesh.FaceMesh(
                static_image_mode=False,
                max_num_faces=1,  # 只检测一张脸
                refine_landmarks=True,  # 细化眼睛和唇部周围的地标
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            
            # 定义关键点索引
            # 眼睛关键点 (依据MediaPipe FaceMesh索引)
            self.left_eye_indices = [33, 160, 158, 133, 153, 144]  # 左眼关键点
            self.right_eye_indices = [362, 385, 387, 263, 373, 380]  # 右眼关键点
            
            # 嘴部关键点
            self.mouth_indices = [61, 37, 267, 269, 291, 405, 314, 17, 84, 181]
            
            logger.info("MediaPipe FaceMesh模型初始化成功")
        
        except ImportError:
            logger.error("无法导入mediapipe库，请安装: pip install mediapipe>=0.10.0")
            self.use_mediapipe = False
        
        except Exception as e:
            logger.error(f"初始化MediaPipe FaceMesh失败: {e}")
            self.use_mediapipe = False
    
    def detect_face(self, frame: np.ndarray) -> Dict[str, Any]:
        """
        检测面部关键点
        
        Args:
            frame: 输入图像
            
        Returns:
            Dict: 面部关键点检测结果
        """
        if not self.use_mediapipe or self.face_mesh is None:
            logger.warning("MediaPipe未启用或初始化失败")
            return {}
        
        try:
            # 将BGR转换为RGB (MediaPipe需要RGB格式)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # 运行检测
            results = self.face_mesh.process(rgb_frame)
            
            # 如果未检测到面部，返回空结果
            if not results.multi_face_landmarks:
                return {}
            
            # 获取第一个面部的关键点
            face_landmarks = results.multi_face_landmarks[0]
            
            # 提取所有关键点坐标
            h, w, _ = frame.shape
            landmarks = []
            for landmark in face_landmarks.landmark:
                x, y = int(landmark.x * w), int(landmark.y * h)
                landmarks.append((x, y))
            
            # 提取特定特征点
            left_eye = [landmarks[i] for i in self.left_eye_indices]
            right_eye = [landmarks[i] for i in self.right_eye_indices]
            mouth = [landmarks[i] for i in self.mouth_indices]
            
            # 计算眼睛和嘴巴的开合比例
            eye_ratio = self._calculate_eye_ratio(left_eye, right_eye)
            mouth_ratio = self._calculate_mouth_ratio(mouth)
            
            return {
                "landmarks": landmarks,       # 所有关键点
                "left_eye": left_eye,         # 左眼关键点
                "right_eye": right_eye,       # 右眼关键点
                "mouth": mouth,               # 嘴巴关键点
                "eye_ratio": eye_ratio,       # 眼睛开合比例
                "mouth_ratio": mouth_ratio    # 嘴巴开合比例
            }
        
        except Exception as e:
            logger.error(f"面部检测过程中出错: {e}")
            return {}
    
    def _calculate_eye_ratio(self, left_eye: List[Tuple[int, int]], right_eye: List[Tuple[int, int]]) -> float:
        """计算眼睛长宽比"""
        def calc_ratio(eye):
            # 计算垂直距离 (平均)
            a = self._distance(eye[1], eye[5])  # 上下眼睑距离1
            b = self._distance(eye[2], eye[4])  # 上下眼睑距离2
            
            # 计算水平距离
            c = self._distance(eye[0], eye[3])  # 眼角距离
            
            # 计算比例 (a+b) / (2.0*c)
            return (a + b) / (2.0 * c) if c > 0 else 0
        
        # 计算左右眼比例并取平均
        left_ratio = calc_ratio(left_eye) if len(left_eye) >= 6 else 0
        right_ratio = calc_ratio(right_eye) if len(right_eye) >= 6 else 0
        
        # 返回平均值
        return (left_ratio + right_ratio) / 2.0 if left_ratio > 0 and right_ratio > 0 else 0
    
    def _calculate_mouth_ratio(self, mouth: List[Tuple[int, int]]) -> float:
        """计算嘴巴长宽比"""
        if len(mouth) < 8:
            return 0
        
        # 计算垂直距离 (平均)
        a = self._distance(mouth[2], mouth[6])  # 上下唇距离1
        b = self._distance(mouth[3], mouth[7])  # 上下唇距离2
        
        # 计算水平距离
        c = self._distance(mouth[0], mouth[4])  # 嘴角距离
        
        # 计算比例 (a+b) / (2.0*c)
        return (a + b) / (2.0 * c) if c > 0 else 0
    
    @staticmethod
    def _distance(p1: Tuple[int, int], p2: Tuple[int, int]) -> float:
        """计算两点之间的欧氏距离"""
        return np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


# 导出全局实例
yolo_detector = YOLODetector()
face_detector = FaceDetector()


if __name__ == "__main__":
    # 测试代码
    import cv2
    
    # 测试图像
    img_path = "test.jpg"
    if not os.path.exists(img_path):
        # 创建一个测试图像
        img = np.zeros((640, 640, 3), dtype=np.uint8)
        cv2.putText(img, "Test Image", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.imwrite(img_path, img)
    
    # 加载图像
    img = cv2.imread(img_path)
    
    # YOLO检测
    results = yolo_detector.detect(img)
    formatted = yolo_detector.format_results(results)
    print(f"YOLO检测结果: {formatted}")
    
    # 面部检测
    face_results = face_detector.detect_face(img)
    if face_results:
        print(f"眼睛开合比: {face_results['eye_ratio']:.3f}")
        print(f"嘴巴开合比: {face_results['mouth_ratio']:.3f}")
    else:
        print("未检测到面部")
