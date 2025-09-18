# 视频处理模块

import cv2
import time
import logging
import numpy as np
from typing import Dict, Any, List, Tuple, Optional

from client.config import config

logger = logging.getLogger("SafePilot.VideoProcessor")

class VideoProcessor:
    """视频处理类 - 负责视频预处理、增强和显示"""
    
    def __init__(self):
        """初始化视频处理器"""
        self.config = config
        self.display_window_name = "SafePilot"
        self.is_window_created = False
        self.last_processed_time = time.time()
        self.frame_count = 0
        
        # 调整参数
        self.brightness = 0
        self.contrast = 1.0
        self.saturation = 1.0
        
        logger.info("VideoProcessor初始化完成")
    
    def preprocess_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        预处理视频帧，用于模型输入
        
        Args:
            frame: 原始视频帧
        
        Returns:
            处理后的视频帧
        """
        # 记录时间
        self.frame_count += 1
        self.last_processed_time = time.time()
        
        # 复制原始帧以避免修改
        processed_frame = frame.copy()
        
        # 图像增强
        processed_frame = self._enhance_image(processed_frame)
        
        # 降低噪声（可选）
        # processed_frame = cv2.GaussianBlur(processed_frame, (5, 5), 0)
        
        return processed_frame
    
    def _enhance_image(self, frame: np.ndarray) -> np.ndarray:
        """图像增强处理"""
        # 转换为浮点类型进行处理
        frame_float = frame.astype(float)
        
        # 亮度调整
        if self.brightness != 0:
            frame_float += self.brightness
        
        # 对比度调整
        if self.contrast != 1.0:
            frame_float = frame_float * self.contrast
        
        # 饱和度调整 (转到HSV空间)
        if self.saturation != 1.0 and len(frame.shape) == 3:
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV).astype(float)
            hsv[:,:,1] = hsv[:,:,1] * self.saturation  # 调整S通道
            frame_float = cv2.cvtColor(np.clip(hsv, 0, 255).astype(np.uint8), cv2.COLOR_HSV2BGR)
        
        # 裁剪值到合法范围并转回uint8
        return np.clip(frame_float, 0, 255).astype(np.uint8)
    
    def display_frame(self, frame: np.ndarray, detections: Optional[Dict[str, Any]] = None) -> None:
        """
        显示处理后的视频帧和检测结果
        
        Args:
            frame: 视频帧
            detections: 检测结果，包含边界框、标签等信息
        """
        if not self.config.video["show_video"]:
            return
        
        # 复制帧以进行绘制
        display_frame = frame.copy()
        
        # 绘制检测结果
        if detections:
            display_frame = self._draw_detections(display_frame, detections)
        
        # 绘制FPS
        if self.config.ui["display_fps"]:
            fps = self._calculate_fps()
            cv2.putText(display_frame, f"FPS: {fps:.1f}", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # 显示视频
        if not self.is_window_created:
            cv2.namedWindow(self.display_window_name, cv2.WINDOW_NORMAL)
            self.is_window_created = True
        
        cv2.imshow(self.display_window_name, display_frame)
        cv2.waitKey(1)  # 必须调用waitKey以更新窗口
    
    def _draw_detections(self, frame: np.ndarray, detections: Dict[str, Any]) -> np.ndarray:
        """在帧上绘制检测结果"""
        # 处理边界框
        if "boxes" in detections:
            for box in detections["boxes"]:
                label = box.get("label", "")
                confidence = box.get("confidence", 0)
                x1, y1, x2, y2 = box.get("xyxy", [0, 0, 0, 0])
                
                # 绘制边界框
                color = (0, 255, 0)  # 默认绿色
                if label.lower() in ["phone", "smoke", "drink"]:
                    color = (0, 0, 255)  # 危险行为用红色
                
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                
                # 绘制标签
                text = f"{label} {confidence:.2f}"
                cv2.putText(frame, text, (int(x1), int(y1) - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # 处理面部关键点
        if "landmarks" in detections:
            landmarks = detections["landmarks"]
            for point in landmarks:
                x, y = point
                cv2.circle(frame, (int(x), int(y)), 2, (0, 255, 255), -1)
            
            # 绘制眼睛轮廓
            if "left_eye" in detections and len(detections["left_eye"]) >= 6:
                self._draw_eye(frame, detections["left_eye"])
            
            if "right_eye" in detections and len(detections["right_eye"]) >= 6:
                self._draw_eye(frame, detections["right_eye"])
            
            # 绘制嘴巴轮廓
            if "mouth" in detections and len(detections["mouth"]) >= 8:
                self._draw_mouth(frame, detections["mouth"])
        
        # 添加状态信息
        if "status" in detections:
            status = detections["status"]
            y_offset = 70
            
            for key, value in status.items():
                if isinstance(value, (int, float)):
                    text = f"{key}: {value:.3f}" if isinstance(value, float) else f"{key}: {value}"
                else:
                    text = f"{key}: {value}"
                
                cv2.putText(frame, text, (10, y_offset), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                y_offset += 30
        
        return frame
    
    def _draw_eye(self, frame: np.ndarray, eye_points: List[Tuple[int, int]]) -> None:
        """绘制眼睛轮廓"""
        # 绘制眼睛轮廓
        eye_hull = cv2.convexHull(np.array(eye_points))
        cv2.drawContours(frame, [eye_hull], -1, (0, 255, 0), 1)
        
        # 绘制垂直线
        if len(eye_points) >= 6:
            # 上下眼睑中点的连线
            cv2.line(frame, 
                    (int(eye_points[1][0]), int(eye_points[1][1])),
                    (int(eye_points[5][0]), int(eye_points[5][1])),
                    (0, 255, 0), 1)
            # 左右眼角的连线
            cv2.line(frame,
                    (int(eye_points[0][0]), int(eye_points[0][1])),
                    (int(eye_points[3][0]), int(eye_points[3][1])),
                    (0, 255, 0), 1)
    
    def _draw_mouth(self, frame: np.ndarray, mouth_points: List[Tuple[int, int]]) -> None:
        """绘制嘴巴轮廓"""
        # 绘制嘴巴轮廓
        mouth_hull = cv2.convexHull(np.array(mouth_points))
        cv2.drawContours(frame, [mouth_hull], -1, (0, 255, 0), 1)
        
        # 绘制垂直和水平线
        if len(mouth_points) >= 8:
            # 上下唇中点的连线
            cv2.line(frame,
                    (int(mouth_points[2][0]), int(mouth_points[2][1])),
                    (int(mouth_points[6][0]), int(mouth_points[6][1])),
                    (0, 255, 0), 1)
            # 左右嘴角的连线
            cv2.line(frame,
                    (int(mouth_points[0][0]), int(mouth_points[0][1])),
                    (int(mouth_points[4][0]), int(mouth_points[4][1])),
                    (0, 255, 0), 1)
    
    def _calculate_fps(self) -> float:
        """计算当前FPS"""
        current_time = time.time()
        elapsed = current_time - self.last_processed_time
        if elapsed < 0.001:  # 避免除以零
            elapsed = 0.001
        return 1.0 / elapsed
    
    def save_frame(self, frame: np.ndarray, filename: str) -> bool:
        """
        保存视频帧到文件
        
        Args:
            frame: 要保存的视频帧
            filename: 保存的文件名
            
        Returns:
            是否保存成功
        """
        try:
            cv2.imwrite(filename, frame)
            logger.info(f"帧保存成功: {filename}")
            return True
        except Exception as e:
            logger.error(f"保存帧失败: {e}")
            return False
    
    def close(self) -> None:
        """关闭窗口和资源"""
        if self.is_window_created:
            cv2.destroyWindow(self.display_window_name)
            self.is_window_created = False
    
    def __del__(self):
        self.close()


if __name__ == "__main__":
    # 测试代码
    from client.video_streamer import VideoStreamer
    import time
    
    streamer = VideoStreamer()
    processor = VideoProcessor()
    
    if streamer.start():
        try:
            for _ in range(200):  # 处理200帧
                ret, frame = streamer.read()
                if ret:
                    processed = processor.preprocess_frame(frame)
                    
                    # 模拟检测结果
                    mock_detections = {
                        "boxes": [
                            {"label": "face", "confidence": 0.95, "xyxy": [100, 100, 300, 300]},
                            {"label": "phone", "confidence": 0.85, "xyxy": [350, 200, 450, 300]}
                        ],
                        "landmarks": [(200, 150), (250, 150), (200, 200), (250, 200)],
                        "status": {
                            "eye_ratio": 0.25,
                            "mouth_ratio": 0.5,
                            "state": "正常"
                        }
                    }
                    
                    processor.display_frame(processed, mock_detections)
                
                time.sleep(0.03)  # 约30fps
        finally:
            streamer.stop()
            processor.close()
    else:
        print("无法启动视频流")
