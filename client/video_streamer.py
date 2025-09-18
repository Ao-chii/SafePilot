# 视频流处理模块

import cv2
import time
import logging
import threading
import queue
import numpy as np
from pathlib import Path
from typing import Union, Optional, Tuple

from client.config import config

logger = logging.getLogger("SafePilot.VideoStreamer")

class VideoStreamer:
    """视频流管理类 - 负责视频的获取、缓存和提供"""
    
    def __init__(self, source: Union[int, str] = None, width: int = None, height: int = None, fps: int = None):
        """
        初始化视频流
        
        Args:
            source: 视频源 (0: 默认摄像头, 1,2...: 其他摄像头, 或视频文件路径)
            width: 视频宽度
            height: 视频高度
            fps: 帧率
        """
        # 使用配置或传入参数
        self.source = source if source is not None else config.video["source"]
        self.width = width if width is not None else config.video["width"]
        self.height = height if height is not None else config.video["height"]
        self.fps = fps if fps is not None else config.video["fps"]
        
        # 视频捕获对象
        self.cap = None
        
        # 帧处理变量
        self.frame_queue = queue.Queue(maxsize=30)  # 帧缓存队列，最多保存30帧
        self.last_frame = None
        self.fps_measured = 0
        self.frame_count = 0
        self.start_time = 0
        
        # 线程控制
        self.is_running = False
        self.thread = None
        
        logger.info(f"VideoStreamer初始化完成，视频源: {self.source}")
    
    def start(self) -> bool:
        """启动视频流处理线程"""
        if self.is_running:
            logger.warning("视频流已经在运行中")
            return True
        
        # 尝试打开视频源
        try:
            self.cap = cv2.VideoCapture(self.source)
            if not self.cap.isOpened():
                logger.error(f"无法打开视频源: {self.source}")
                return False
            
            # 设置视频参数
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.cap.set(cv2.CAP_PROP_FPS, self.fps)
            
            # 读取实际设置的参数
            self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.fps = self.cap.get(cv2.CAP_PROP_FPS)
            
            logger.info(f"视频流打开成功: {self.width}x{self.height} @ {self.fps}fps")
            
            # 启动捕获线程
            self.is_running = True
            self.start_time = time.time()
            self.thread = threading.Thread(target=self._capture_loop, daemon=True)
            self.thread.start()
            
            return True
        
        except Exception as e:
            logger.error(f"启动视频流失败: {e}")
            if self.cap is not None:
                self.cap.release()
                self.cap = None
            return False
    
    def _capture_loop(self):
        """视频捕获循环"""
        while self.is_running:
            if not self.cap.isOpened():
                logger.error("视频流已关闭")
                self.is_running = False
                break
            
            ret, frame = self.cap.read()
            if not ret:
                logger.warning("视频帧读取失败")
                # 如果是视频文件，可能到达末尾，尝试重新开始
                if isinstance(self.source, str) and Path(self.source).is_file():
                    logger.info("尝试重新开始视频文件")
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                else:
                    # 对于摄像头，等待一段时间后重试
                    time.sleep(1)
                    continue
            
            # 更新帧计数和FPS
            self.frame_count += 1
            elapsed = time.time() - self.start_time
            if elapsed > 0:
                self.fps_measured = self.frame_count / elapsed
            
            # 每秒重置一次计数
            if elapsed >= 1.0:
                self.start_time = time.time()
                self.frame_count = 0
            
            # 保存当前帧
            self.last_frame = frame.copy()
            
            # 将帧放入队列，如果队列已满则丢弃最旧的帧
            if self.frame_queue.full():
                try:
                    self.frame_queue.get_nowait()
                except queue.Empty:
                    pass
            
            try:
                self.frame_queue.put_nowait(frame)
            except queue.Full:
                pass
    
    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        读取最新的视频帧
        
        Returns:
            Tuple[bool, Optional[np.ndarray]]: (成功标志, 视频帧)
        """
        if not self.is_running:
            return False, None
        
        try:
            frame = self.frame_queue.get_nowait()
            return True, frame
        except queue.Empty:
            # 如果队列为空，返回最后一帧
            if self.last_frame is not None:
                return True, self.last_frame.copy()
            return False, None
    
    def stop(self):
        """停止视频流"""
        self.is_running = False
        
        if self.thread is not None:
            self.thread.join(timeout=1.0)
            self.thread = None
        
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        
        logger.info("视频流已停止")
    
    def is_opened(self) -> bool:
        """检查视频流是否打开"""
        return self.is_running and self.cap is not None and self.cap.isOpened()
    
    def get_fps(self) -> float:
        """获取当前测量的FPS"""
        return self.fps_measured
    
    def __del__(self):
        self.stop()


if __name__ == "__main__":
    # 测试代码
    import time
    
    streamer = VideoStreamer()
    if streamer.start():
        try:
            while True:
                ret, frame = streamer.read()
                if ret:
                    # 显示FPS信息
                    cv2.putText(frame, f"FPS: {streamer.get_fps():.2f}", (10, 30), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    cv2.imshow("Video Stream", frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                time.sleep(0.01)  # 小延迟以减少CPU使用率
        finally:
            streamer.stop()
            cv2.destroyAllWindows()
    else:
        print("无法启动视频流")
