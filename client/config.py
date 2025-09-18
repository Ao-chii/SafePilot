# 客户端配置模块

import os
import json
from pathlib import Path
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("SafePilot")

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent.absolute()
WEIGHTS_DIR = ROOT_DIR / "weights"
DATA_DIR = ROOT_DIR / "data"
LOGS_DIR = ROOT_DIR / "logs"

# 确保目录存在
os.makedirs(WEIGHTS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)


class Config:
    """配置类 - 单例模式"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._load_default_config()
        return cls._instance
    
    def _load_default_config(self):
        """加载默认配置"""
        self.server_url = "http://localhost:5000"  # 服务器地址
        
        # 设备标识
        self.device_id = "default_device"
        self.driver_id = "default_driver"
        
        # 模型配置
        self.model = {
            "yolo_model": str(WEIGHTS_DIR / "best.pt"),  # YOLOv11模型
            "fallback_model": "yolov11s.pt",             # 备用模型
            "facemesh_model": True,                      # 是否使用MediaPipe面部检测
            "device": "auto",                            # 推理设备 (auto/cpu/0/1...)
            "conf_threshold": 0.6,                       # 检测置信度阈值
            "iou_threshold": 0.45,                       # NMS IoU阈值
            "img_size": 640,                             # 输入图像大小
        }
        
        # 视频配置
        self.video = {
            "source": 0,                # 视频源 (0: 默认摄像头, 1,2...: 其他摄像头, 或视频文件路径)
            "width": 640,               # 视频宽度
            "height": 480,              # 视频高度
            "fps": 30,                  # 帧率
            "show_video": True,         # 是否显示视频
        }
        
        # 危险行为检测配置
        self.behavior = {
            # 疲劳检测
            "eye_ar_threshold": 0.15,       # 眼睛长宽比阈值
            "eye_ar_consec_frames": 2,      # 连续闭眼帧数阈值
            "mouth_ar_threshold": 0.65,     # 打哈欠长宽比阈值
            "mouth_ar_consec_frames": 3,    # 连续张嘴帧数阈值
            "perclos_window": 150,          # PERCLOS计算窗口大小(帧数)
            "perclos_threshold": 0.38,      # 疲劳判断阈值
            "mouth_weight": 0.2,            # 嘴巴在PERCLOS模型中的权重
            
            # 分心检测
            "distraction_window": 15,       # 分心行为检测窗口大小
            "head_pose_threshold": 30,      # 头部姿态阈值(度)
            
            # 危险行为识别
            "phone_enabled": True,          # 是否检测手机使用
            "smoke_enabled": True,          # 是否检测抽烟
            "drink_enabled": True,          # 是否检测喝水
            "yawn_enabled": True,           # 是否检测打哈欠
            "eyes_closed_enabled": True,    # 是否检测闭眼
        }
        
        # 报警配置
        self.alarm = {
            "visual_alarm": True,           # 是否启用视觉报警
            "sound_alarm": True,            # 是否启用声音报警
            "sound_volume": 0.8,            # 声音报警音量 (0.0-1.0)
            "alarm_cooldown": 5,            # 报警冷却时间(秒)
            "save_alarm_image": True,       # 是否保存报警图像
            "max_alarm_images": 100,        # 最大报警图像数量
        }
        
        # 数据上传配置
        self.upload = {
            "enabled": False,               # 是否启用数据上传
            "upload_interval": 60,          # 上传间隔(秒)
            "retry_interval": 10,           # 重试间隔(秒)
            "max_retries": 3,               # 最大重试次数
            "buffer_size": 1000,            # 本地缓存大小
        }
        
        # UI配置
        self.ui = {
            "window_title": "SafePilot - 驾驶员危险行为检测系统",
            "update_interval": 20,          # UI更新间隔(毫秒)
            "display_fps": True,            # 是否显示FPS
            "display_debug_info": True,     # 是否显示调试信息
        }
        
        # 尝试从配置文件加载自定义配置
        self._load_from_file()
    
    def _load_from_file(self, config_file="config.json"):
        """从文件加载配置"""
        config_path = Path(config_file)
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    custom_config = json.load(f)
                    self._update_config(custom_config)
                    logger.info(f"已加载配置文件: {config_path}")
            except Exception as e:
                logger.error(f"加载配置文件失败: {e}")
    
    def _update_config(self, custom_config):
        """递归更新配置"""
        for key, value in custom_config.items():
            if hasattr(self, key):
                if isinstance(value, dict) and isinstance(getattr(self, key), dict):
                    getattr(self, key).update(value)
                else:
                    setattr(self, key, value)
    
    def save(self, config_file="config.json"):
        """保存配置到文件"""
        try:
            config_dict = {
                "server_url": self.server_url,
                "device_id": self.device_id,
                "driver_id": self.driver_id,
                "model": self.model,
                "video": self.video,
                "behavior": self.behavior,
                "alarm": self.alarm,
                "upload": self.upload,
                "ui": self.ui
            }
            
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(config_dict, f, indent=4, ensure_ascii=False)
            logger.info(f"配置已保存到: {config_file}")
            return True
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
            return False

# 全局配置实例
config = Config()

if __name__ == "__main__":
    # 测试配置加载和保存
    print(f"服务器地址: {config.server_url}")
    print(f"YOLO模型路径: {config.model['yolo_model']}")
    print(f"眼睛长宽比阈值: {config.behavior['eye_ar_threshold']}")
    
    # 保存配置
    config.save("test_config.json")
