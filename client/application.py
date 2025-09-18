# 客户端应用程序 - 整合所有组件

import os
import sys
import time
import logging
import threading
import cv2
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

from client.config import config
from client.video_streamer import VideoStreamer
from client.video_processor import VideoProcessor
from client.detector import yolo_detector, face_detector
from client.analyzer import behavior_analyzer, BehaviorType
from client.alarm_manager import alarm_manager
from client.data_uploader import data_uploader

logger = logging.getLogger("SafePilot.Application")

class SafePilotApp:
    """SafePilot客户端应用程序"""
    
    def __init__(self):
        """初始化应用程序"""
        self.config = config
        
        # 组件实例
        self.video_streamer = VideoStreamer()
        self.video_processor = VideoProcessor()
        self.analyzer = behavior_analyzer
        self.alarm_manager = alarm_manager
        self.data_uploader = data_uploader
        
        # 注册观察者
        self.analyzer.add_observer(self.alarm_manager)
        self.analyzer.add_observer(self.data_uploader)
        
        # 应用状态
        self.is_running = False
        self.paused = False
        self.frame_count = 0
        self.start_time = 0
        self.fps = 0
        self.processing_times = []
        
        # UI事件回调
        self.on_frame_processed = None
        
        logger.info("SafePilotApp初始化完成")
    
    def start(self) -> bool:
        """启动应用程序"""
        if self.is_running:
            logger.warning("应用程序已经在运行")
            return True
        
        try:
            # 启动视频流
            if not self.video_streamer.start():
                logger.error("启动视频流失败")
                return False
            
            # 设置运行状态
            self.is_running = True
            self.paused = False
            self.start_time = time.time()
            
            # 创建检测线程
            self.detection_thread = threading.Thread(target=self._detection_loop, daemon=True)
            self.detection_thread.start()
            
            logger.info("SafePilotApp启动成功")
            return True
        
        except Exception as e:
            logger.error(f"启动应用程序失败: {e}")
            self.stop()
            return False
    
    def stop(self) -> None:
        """停止应用程序"""
        # 设置停止标志
        self.is_running = False
        
        try:
            # 停止视频流
            if self.video_streamer:
                self.video_streamer.stop()
            
            # 关闭处理器
            if self.video_processor:
                self.video_processor.close()
            
            # 等待线程结束
            if hasattr(self, 'detection_thread') and self.detection_thread.is_alive():
                self.detection_thread.join(timeout=2.0)
            
            # 关闭其他组件
            self.data_uploader.shutdown()
            
            logger.info("SafePilotApp已停止")
        
        except Exception as e:
            logger.error(f"停止应用程序时发生错误: {e}")
    
    def pause(self) -> None:
        """暂停应用程序"""
        self.paused = True
        logger.info("应用程序已暂停")
    
    def resume(self) -> None:
        """恢复应用程序"""
        self.paused = False
        logger.info("应用程序已恢复")
    
    def _detection_loop(self) -> None:
        """检测循环"""
        while self.is_running:
            if self.paused:
                time.sleep(0.1)
                continue
            
            try:
                loop_start = time.time()
                
                # 读取视频帧
                ret, frame = self.video_streamer.read()
                if not ret or frame is None:
                    logger.warning("读取视频帧失败")
                    time.sleep(0.1)
                    continue
                
                # 预处理帧
                processed_frame = self.video_processor.preprocess_frame(frame)
                
                # YOLO目标检测
                yolo_results = yolo_detector.detect(processed_frame)
                
                # 面部关键点检测
                face_results = face_detector.detect_face(processed_frame)
                
                # 合并检测结果
                detections = {**yolo_results, **face_results}
                
                # 格式化YOLO检测结果
                if "boxes" in yolo_results:
                    formatted_boxes = yolo_detector.format_results(yolo_results)
                    detections["formatted_boxes"] = formatted_boxes
                
                # 行为分析
                analysis_results = self.analyzer.analyze(processed_frame, detections)
                
                # 获取当前报警状态
                alarm_state = self.alarm_manager.get_active_alarm()
                
                # 如果有活动报警且启用了保存报警图像
                if alarm_state["active"]:
                    behavior_type = alarm_state["type"]
                    # 保存报警图像
                    self.alarm_manager.save_alarm_image(processed_frame, behavior_type)
                
                # 显示处理后的视频帧
                display_data = {
                    **detections,
                    "status": analysis_results["status"],
                    "alarm": alarm_state
                }
                
                # 在UI线程中显示
                if self.on_frame_processed:
                    self.on_frame_processed(processed_frame, display_data)
                else:
                    self.video_processor.display_frame(processed_frame, display_data)
                
                # 计算FPS
                self.frame_count += 1
                processing_time = time.time() - loop_start
                self.processing_times.append(processing_time)
                
                # 保留最近100帧的处理时间
                if len(self.processing_times) > 100:
                    self.processing_times.pop(0)
                
                # 计算平均FPS
                avg_time = sum(self.processing_times) / len(self.processing_times)
                self.fps = 1.0 / avg_time if avg_time > 0 else 0
                
                # 延时，确保不会占用过多CPU
                elapsed = time.time() - loop_start
                sleep_time = max(0.001, (1.0 / 30) - elapsed)  # 目标30fps
                time.sleep(sleep_time)
            
            except Exception as e:
                logger.error(f"检测循环中发生错误: {e}")
                time.sleep(0.5)  # 出错后等待较长时间
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取应用状态
        
        Returns:
            Dict[str, Any]: 状态信息
        """
        return {
            "is_running": self.is_running,
            "paused": self.paused,
            "fps": round(self.fps, 1),
            "frame_count": self.frame_count,
            "run_time": round(time.time() - self.start_time, 1) if self.start_time > 0 else 0,
            "camera_status": self.video_streamer.is_opened(),
            "upload_status": self.data_uploader.get_status(),
            "alarm_active": self.alarm_manager.is_alarm_active
        }


# 创建全局应用实例
app = SafePilotApp()

if __name__ == "__main__":
    # 测试代码 - 直接运行应用程序
    try:
        # 启动应用
        if app.start():
            print("按 'q' 键退出")
            
            # 主循环
            while app.is_running:
                # 显示状态
                if app.frame_count % 30 == 0:  # 每30帧显示一次
                    status = app.get_status()
                    print(f"FPS: {status['fps']}, 运行时间: {status['run_time']}秒")
                
                # 检查键盘事件
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('p'):
                    if app.paused:
                        app.resume()
                    else:
                        app.pause()
                    print("暂停状态切换: ", app.paused)
                
                time.sleep(0.01)
        
        else:
            print("启动应用程序失败")
    
    except KeyboardInterrupt:
        print("程序被用户中断")
    
    finally:
        # 停止应用
        app.stop()
        cv2.destroyAllWindows()
        print("应用程序已退出")
