"""
帧捕获模块
负责从摄像头、视频文件或网络流中稳定地读取帧
"""

import cv2
from queue import Queue
import threading
import time


class FrameCapture:
    """
    帧捕获类
    使用独立线程读取视频帧，避免I/O阻塞主流程
    """
    
    def __init__(self, source=0, frame_queue_maxsize=2):
        """
        初始化帧捕获器
        
        Args:
            source: 视频源，可以是摄像头ID（如0）、视频文件路径或RTSP流地址
            frame_queue_maxsize: 帧队列最大长度
        """
        self.cap = cv2.VideoCapture(source)
        self.frame_queue = Queue(maxsize=frame_queue_maxsize)
        self.running = False
        self.thread = None
        
        # 设置摄像头参数
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # 减少缓冲以获取最新帧
        
    def start(self):
        """
        启动帧捕获线程
        """
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._update_frame, daemon=True)
            self.thread.start()
    
    def _update_frame(self):
        """
        在独立线程中持续读取视频帧
        """
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                # 读取失败，可能是视频结束或摄像头断开
                time.sleep(0.01)  # 短暂休眠避免CPU占用过高
                continue
            
            # 如果队列满了，移除旧帧，放入新帧
            if self.frame_queue.full():
                try:
                    self.frame_queue.get_nowait()
                except:
                    pass
            
            self.frame_queue.put(frame)
            # 控制帧率，避免过度占用CPU
            time.sleep(0.03)
    
    def get_frame(self, timeout=1.0):
        """
        获取一帧图像
        
        Args:
            timeout (float): 超时时间（秒）
            
        Returns:
            frame: 视频帧，如果超时则返回None
        """
        try:
            return self.frame_queue.get(timeout=timeout)
        except:
            return None
    
    def stop(self):
        """
        停止帧捕获
        """
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join()
        self.cap.release()