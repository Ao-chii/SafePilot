#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
驾驶员行为检测与上报系统主程序
整合所有模块，形成完整的工作流
"""

import cv2
import time
import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from frame_capture import FrameCapture
from detector_yolo import YOLODetector
from analyzer_mediapipe import MediaPipeAnalyzer
from behavior_engine import BehaviorEngine
from reporter import Reporter


def main():
    """
    主函数
    """
    print("驾驶员行为检测与上报系统启动中...")
    
    try:
        # 1. 加载配置
        config = Config('config.yaml')
        print("配置加载成功")
        
        # 2. 初始化各个模块
        camera_config = config.get_camera_config()
        frame_capture = FrameCapture(camera_config.get('source', 0))
        frame_capture.start()
        print("摄像头初始化成功")
        
        yolo_config = config.get_yolo_config()
        yolo_detector = YOLODetector(
            yolo_config.get('model_path', 'yolo11n.pt'),
            yolo_config.get('confidence_threshold', 0.5),
            yolo_config.get('classes_to_detect')
        )
        print("YOLO检测器初始化成功")
        
        mp_config = config.get_mediapipe_config()
        mp_analyzer = MediaPipeAnalyzer(
            static_image_mode=mp_config.get('static_image_mode', False),
            max_num_faces=mp_config.get('max_num_faces', 1),
            min_detection_confidence=mp_config.get('min_detection_confidence', 0.5)
        )
        print("MediaPipe分析器初始化成功")
        
        behavior_engine = BehaviorEngine(config)
        print("行为判断引擎初始化成功")
        
        reporter = Reporter(config)
        print("事件报告器初始化成功")
        
        print("系统启动完成，开始检测驾驶员行为。按 'q' 键退出程序。")
        
        # 3. 主循环
        while True:
            # 获取一帧图像
            frame = frame_capture.get_frame()
            if frame is None:
                time.sleep(0.01)  # 短暂休眠避免CPU占用过高
                continue
            
            # YOLO检测
            yolo_detections, annotated_frame = yolo_detector.detect(frame)
            
            # MediaPipe分析
            mp_results = mp_analyzer.analyze(frame)
            
            # 行为判断（传递frame参数以在视频中显示疲劳信息）
            events = behavior_engine.process(yolo_detections, mp_results, annotated_frame)
            
            # 处理事件（报警和上报）
            if events:
                reporter.handle_events(events, annotated_frame)
            
            # 显示结果（可选）
            cv2.imshow('Driver Monitoring', annotated_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
            # 控制处理频率，避免过高CPU占用
            time.sleep(0.03)  # ~30 FPS
    
    except KeyboardInterrupt:
        print("\n用户中断程序执行")
    except Exception as e:
        print(f"程序执行过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 清理资源
        print("正在关闭系统...")
        try:
            frame_capture.stop()
        except:
            pass
        
        try:
            cv2.destroyAllWindows()
        except:
            pass
        
        print("系统已关闭")


if __name__ == "__main__":
    main()