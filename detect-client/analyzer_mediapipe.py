"""
MediaPipe分析模块
封装MediaPipe，提取驾驶员的面部、手部和姿态关键点
"""

import cv2
import numpy as np

try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    print("警告: 未安装mediapipe库，MediaPipe分析功能不可用")


class MediaPipeAnalyzer:
    """
    MediaPipe分析器类
    负责使用MediaPipe提取面部、手部和姿态关键点
    """
    
    def __init__(self, static_image_mode=False, max_num_faces=1, min_detection_confidence=0.5):
        """
        初始化MediaPipe分析器
        
        Args:
            static_image_mode (bool): 是否使用静态图像模式
            max_num_faces (int): 最大检测人脸数
            min_detection_confidence (float): 最小检测置信度
        """
        if not MEDIAPIPE_AVAILABLE:
            raise RuntimeError("MediaPipe功能不可用，请安装mediapipe库: pip install mediapipe")
        
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_hands = mp.solutions.hands
        self.mp_pose = mp.solutions.pose
        
        # 初始化面部网格检测器
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=static_image_mode,
            max_num_faces=max_num_faces,
            refine_landmarks=True,  # 启用眼球和嘴唇精细 landmarks
            min_detection_confidence=min_detection_confidence
        )
        
        # 初始化手部检测器
        self.hands = self.mp_hands.Hands(
            static_image_mode=static_image_mode,
            max_num_hands=2,
            min_detection_confidence=min_detection_confidence
        )
        
        # 初始化姿态检测器
        self.pose = self.mp_pose.Pose(
            static_image_mode=static_image_mode,
            model_complexity=1,
            min_detection_confidence=min_detection_confidence
        )
    
    def analyze(self, frame):
        """
        分析视频帧，提取关键点信息
        
        Args:
            frame: 输入视频帧
            
        Returns:
            dict: 包含面部、手部和姿态分析结果的字典
        """
        # 转换颜色空间（MediaPipe需要RGB格式）
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # 执行分析
        results = {
            'face': self.face_mesh.process(rgb_frame),
            'hands': self.hands.process(rgb_frame),
            'pose': self.pose.process(rgb_frame)
        }
        
        return results
    

    
    def estimate_gaze_direction(self, face_landmarks):
        """
        估算视线方向（简化实现）
        
        Args:
            face_landmarks: 面部关键点
            
        Returns:
            tuple: (水平视线方向, 垂直视线方向)
        """
        # 这里是一个简化的视线方向估算
        # 实际应用中需要更复杂的几何计算
        if not face_landmarks:
            return 0.0, 0.0
        
        # 使用面部关键点估算头部姿态，进而推断视线方向
        # 这里仅作示意，实际实现需要更复杂的计算
        return 0.0, 0.0