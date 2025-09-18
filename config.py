# SafePilot 配置文件
# YOLOv11检测器和疲劳检测相关配置

import os

class YOLOConfig:
    """YOLOv11检测器配置类"""
    
    def __init__(self):
        # 模型配置
        self.model_path = 'weights/best.pt'  # 自定义模型路径
        self.fallback_model = 'yolo11s.pt'   # 备用预训练模型
        
        # 检测参数
        self.conf_thres = 0.6      # 置信度阈值
        self.iou_thres = 0.45      # NMS IoU阈值
        self.imgsz = 640           # 输入图像大小
        
        # 设备配置
        self.device = 'auto'       # 设备选择 ('auto', 'cpu', '0', '1', etc.)
        
        # 支持的目标类别 (根据你的训练数据调整)
        self.target_classes = ['face', 'phone', 'smoke', 'drink']
        
        # 性能配置
        self.enable_warmup = True   # 启用模型预热
        self.verbose = False        # 是否显示详细输出

    def get_available_models(self):
        """获取可用的YOLOv11模型"""
        models = {
            'yolo11n.pt': 'YOLOv11 Nano (最快)',
            'yolo11s.pt': 'YOLOv11 Small (平衡)',
            'yolo11m.pt': 'YOLOv11 Medium (更准确)',
            'yolo11l.pt': 'YOLOv11 Large (高精度)',
            'yolo11x.pt': 'YOLOv11 XLarge (最高精度)'
        }
        return models
    
    def validate_config(self):
        """验证配置有效性"""
        errors = []
        
        # 检查置信度阈值
        if not 0.0 <= self.conf_thres <= 1.0:
            errors.append("置信度阈值必须在0.0-1.0之间")
        
        # 检查IoU阈值  
        if not 0.0 <= self.iou_thres <= 1.0:
            errors.append("IoU阈值必须在0.0-1.0之间")
            
        # 检查图像大小
        if self.imgsz <= 0 or self.imgsz % 32 != 0:
            errors.append("图像大小必须是32的倍数且大于0")
            
        return errors


class FatigueConfig:
    """疲劳检测配置类"""
    
    def __init__(self):
        # 眼睛检测参数
        self.eye_ar_thresh = 0.15        # 眼睛长宽比阈值
        self.eye_ar_consec_frames = 2    # 连续闭眼帧数阈值
        
        # 嘴巴检测参数  
        self.mouth_ar_thresh = 0.65      # 打哈欠长宽比阈值
        self.mouth_ar_consec_frames = 3  # 连续张嘴帧数阈值
        
        # 疲劳模型参数
        self.perclos_window = 150        # PERCLOS计算窗口大小(帧数)
        self.perclos_thresh = 0.38       # 疲劳判断阈值
        self.mouth_weight = 0.2          # 嘴巴在PERCLOS模型中的权重
        
        # Dlib模型文件
        self.landmark_model = 'weights/shape_predictor_68_face_landmarks.dat'
        
        # 分心行为检测
        self.distraction_window = 15     # 分心行为检测窗口大小


class AppConfig:
    """应用程序配置类"""
    
    def __init__(self):
        # UI配置
        self.window_title = "SafePilot - 安全驾驶监测系统"
        self.camera_index = 0            # 默认摄像头索引
        self.timer_interval = 20         # 视频帧更新间隔(毫秒)
        
        # 路径配置
        self.weights_dir = 'weights'     # 权重文件目录
        self.log_dir = 'logs'            # 日志文件目录
        
        # 创建必要目录
        self._create_directories()
    
    def _create_directories(self):
        """创建必要的目录"""
        dirs = [self.weights_dir, self.log_dir]
        for dir_path in dirs:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
                print(f"创建目录: {dir_path}")


# 全局配置实例
yolo_config = YOLOConfig()
fatigue_config = FatigueConfig()
app_config = AppConfig()


def load_config_from_file(config_file='config.ini'):
    """从配置文件加载设置"""
    # TODO: 实现从INI文件或JSON文件加载配置
    pass


def save_config_to_file(config_file='config.ini'):
    """保存配置到文件"""  
    # TODO: 实现配置保存功能
    pass


def get_yolo_config():
    """获取YOLO配置"""
    return yolo_config


def get_fatigue_config():
    """获取疲劳检测配置"""
    return fatigue_config


def get_app_config():
    """获取应用程序配置"""
    return app_config


if __name__ == '__main__':
    # 配置验证测试
    print("=== SafePilot配置验证 ===")
    
    errors = yolo_config.validate_config()
    if errors:
        print("YOLO配置错误:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✓ YOLO配置有效")
    
    print(f"✓ 可用模型: {list(yolo_config.get_available_models().keys())}")
    print(f"✓ 当前模型路径: {yolo_config.model_path}")
    print(f"✓ 备用模型: {yolo_config.fallback_model}")
    print(f"✓ 疲劳检测阈值: {fatigue_config.perclos_thresh}")
