#!/usr/bin/env python3
# SafePilot 客户端启动脚本

import os
import sys
import cv2
import time
import argparse
import logging
from pathlib import Path

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('safepilot.log')
    ]
)
logger = logging.getLogger("SafePilot")

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='SafePilot 驾驶员危险行为检测系统')
    
    parser.add_argument('--camera', type=int, default=0,
                       help='摄像头索引 (默认: 0)')
    
    parser.add_argument('--video', type=str, default=None,
                       help='视频文件路径，优先于摄像头')
    
    parser.add_argument('--model', type=str, default='weights/best.pt',
                       help='YOLOv11模型路径 (默认: weights/best.pt)')
    
    parser.add_argument('--device', type=str, default='auto',
                       help='设备 (auto/cpu/0/1/2/...) (默认: auto)')
    
    parser.add_argument('--conf', type=float, default=0.6,
                       help='置信度阈值 (默认: 0.6)')
    
    parser.add_argument('--upload', action='store_true',
                       help='启用数据上传')
    
    parser.add_argument('--server', type=str, default=None,
                       help='服务器URL (例如: http://localhost:5000)')
    
    parser.add_argument('--config', type=str, default=None,
                       help='配置文件路径')
    
    return parser.parse_args()

def main():
    """主函数"""
    # 解析命令行参数
    args = parse_args()
    
    # 导入客户端应用
    try:
        from client.application import app
        from client.config import config
    except ImportError:
        logger.error("无法导入客户端模块，请确保安装了所有依赖")
        sys.exit(1)
    
    # 应用命令行参数
    if args.video:
        if os.path.exists(args.video):
            config.video["source"] = args.video
        else:
            logger.error(f"视频文件不存在: {args.video}")
            sys.exit(1)
    else:
        config.video["source"] = args.camera
    
    if args.model:
        config.model["yolo_model"] = args.model
    
    if args.device:
        config.model["device"] = args.device
    
    if args.conf:
        config.model["conf_threshold"] = args.conf
    
    if args.upload:
        config.upload["enabled"] = True
    
    if args.server:
        config.server_url = args.server
    
    # 加载自定义配置文件
    if args.config and os.path.exists(args.config):
        try:
            # 创建配置类的新实例并加载配置
            config._load_from_file(args.config)
            logger.info(f"已加载配置文件: {args.config}")
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
    
    logger.info("启动SafePilot客户端...")
    logger.info(f"视频源: {config.video['source']}")
    logger.info(f"YOLO模型: {config.model['yolo_model']}")
    logger.info(f"设备: {config.model['device']}")
    
    try:
        # 启动应用
        if app.start():
            print("\n=== SafePilot 驾驶员危险行为检测系统 ===")
            print("按 'q' 退出, 'p' 暂停/恢复")
            
            # 主循环
            while app.is_running:
                # 显示状态
                if app.frame_count % 100 == 0:  # 每100帧显示一次
                    status = app.get_status()
                    fps = status["fps"]
                    runtime = status["run_time"]
                    print(f"FPS: {fps:.1f}, 运行时间: {runtime:.1f}秒")
                
                # 检查键盘事件
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('p'):
                    if app.paused:
                        app.resume()
                    else:
                        app.pause()
                    print("暂停状态切换: ", "已暂停" if app.paused else "运行中")
                
                time.sleep(0.01)
        
        else:
            print("启动应用程序失败")
            return 1
    
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    
    except Exception as e:
        logger.error(f"运行时发生错误: {e}")
        return 1
    
    finally:
        # 停止应用
        print("正在关闭应用程序...")
        app.stop()
        cv2.destroyAllWindows()
        print("应用程序已退出")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
