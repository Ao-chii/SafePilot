"""
配置管理模块
用于加载和管理系统的配置参数
"""

import yaml
import os


class Config:
    """
    配置管理类
    负责加载和提供配置参数
    """
    def __init__(self, config_path='config.yaml'):
        """
        初始化配置管理器
        
        Args:
            config_path (str): 配置文件路径
        """
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"配置文件 {config_path} 不存在")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self._config = yaml.safe_load(f)
    
    def get(self, key_path, default=None):
        """
        获取配置项的值
        
        Args:
            key_path (str): 配置项路径，如 'camera.source'
            default: 默认值
            
        Returns:
            配置项的值
        """
        keys = key_path.split('.')
        value = self._config
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_camera_config(self):
        """获取摄像头配置"""
        return self._config.get('camera', {})
    
    def get_yolo_config(self):
        """获取YOLO配置"""
        return self._config.get('yolo', {})
    
    def get_self_yolo_config(self):
        """获取自己训练的YOLO配置"""
        return self._config.get('self_yolo', {})

    def get_mediapipe_config(self):
        """获取MediaPipe配置"""
        return self._config.get('mediapipe', {})
    
    def get_behavior_rules_config(self):
        """获取行为规则配置"""
        return self._config.get('behavior_rules', {})
    
    def get_server_config(self):
        """获取服务器配置"""
        return self._config.get('server', {})
    
    def get_driver_config(self):
        """获取司机配置"""
        return self._config.get('driver', {})