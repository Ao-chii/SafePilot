# 报警管理模块 - 处理系统报警

import os
import time
import logging
import threading
import numpy as np
import cv2
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

from client.analyzer import BehaviorObserver, BehaviorType
from client.config import config, DATA_DIR

logger = logging.getLogger("SafePilot.AlarmManager")

# 创建报警图像存储目录
ALARM_DIR = DATA_DIR / "alarms"
os.makedirs(ALARM_DIR, exist_ok=True)


class AlarmManager(BehaviorObserver):
    """报警管理器 - 观察者模式，接收行为分析器的通知"""
    
    def __init__(self):
        """初始化报警管理器"""
        self.config = config.alarm
        
        # 报警配置
        self.visual_alarm = self.config["visual_alarm"]
        self.sound_alarm = self.config["sound_alarm"]
        self.sound_volume = self.config["sound_volume"]
        self.alarm_cooldown = self.config["alarm_cooldown"]
        self.save_alarm_image = self.config["save_alarm_image"]
        self.max_alarm_images = self.config["max_alarm_images"]
        
        # 报警状态
        self.is_alarm_active = False
        self.current_alarm_type = None
        self.alarm_start_time = 0
        self.last_alarm_time = {}  # 各类型行为的最后报警时间
        
        # 声音播放器
        self.sound_player = None
        self._init_sound_player()
        
        # 保存的报警图像计数
        self.alarm_image_count = 0
        self._count_existing_alarm_images()
        
        # 线程锁
        self.lock = threading.RLock()
        
        logger.info("AlarmManager初始化完成")
    
    def _init_sound_player(self):
        """初始化声音播放器"""
        try:
            import pygame
            pygame.mixer.init()
            self.sound_player = pygame
            logger.info("声音播放器初始化成功")
        except ImportError:
            logger.warning("无法导入pygame，声音报警将不可用")
            self.sound_player = None
        except Exception as e:
            logger.error(f"初始化声音播放器失败: {e}")
            self.sound_player = None
    
    def _count_existing_alarm_images(self):
        """计算已存在的报警图像数量"""
        if os.path.exists(ALARM_DIR):
            image_files = list(ALARM_DIR.glob("alarm_*.jpg"))
            self.alarm_image_count = len(image_files)
            logger.info(f"已存在{self.alarm_image_count}张报警图像")
    
    def on_behavior_detected(self, behavior_type: str, confidence: float, details: Dict[str, Any]) -> None:
        """
        接收行为检测通知并触发报警
        
        Args:
            behavior_type: 行为类型
            confidence: 置信度
            details: 详细信息
        """
        # 检查报警冷却时间
        current_time = time.time()
        last_time = self.last_alarm_time.get(behavior_type, 0)
        if current_time - last_time < self.alarm_cooldown:
            # 在冷却期内，不重复触发相同类型的报警
            return
        
        # 更新最后报警时间
        self.last_alarm_time[behavior_type] = current_time
        
        # 根据行为类型确定报警消息和级别
        alarm_message, alarm_level = self._get_alarm_info(behavior_type)
        
        # 触发报警
        self._trigger_alarm(behavior_type, alarm_message, alarm_level, confidence)
        
        logger.info(f"触发报警: {behavior_type}, 置信度: {confidence:.2f}, 级别: {alarm_level}")
    
    def _get_alarm_info(self, behavior_type: str) -> Tuple[str, int]:
        """
        根据行为类型获取报警消息和级别
        
        Args:
            behavior_type: 行为类型
            
        Returns:
            Tuple[str, int]: (报警消息, 报警级别)
        """
        # 报警级别: 1-低, 2-中, 3-高
        if behavior_type == BehaviorType.EYES_CLOSED:
            return "检测到闭眼，请保持警觉！", 2
        
        elif behavior_type == BehaviorType.YAWN:
            return "检测到打哈欠，注意休息！", 1
        
        elif behavior_type == BehaviorType.DROWSY:
            return "您可能处于疲劳状态，建议停车休息！", 3
        
        elif behavior_type == BehaviorType.PHONE_USE:
            return "检测到使用手机，请专心驾驶！", 3
        
        elif behavior_type == BehaviorType.SMOKING:
            return "检测到吸烟行为，请专心驾驶！", 2
        
        elif behavior_type == BehaviorType.DRINKING:
            return "检测到喝水行为，请注意安全！", 1
        
        else:
            return f"检测到危险行为: {behavior_type}", 2
    
    def _trigger_alarm(self, behavior_type: str, message: str, level: int, confidence: float) -> None:
        """
        触发报警
        
        Args:
            behavior_type: 行为类型
            message: 报警消息
            level: 报警级别
            confidence: 置信度
        """
        with self.lock:
            self.is_alarm_active = True
            self.current_alarm_type = behavior_type
            self.alarm_start_time = time.time()
            
            # 视觉报警将在界面上显示
            if self.visual_alarm:
                # 视觉报警由UI处理，这里只记录状态
                pass
            
            # 声音报警
            if self.sound_alarm and self.sound_player:
                self._play_alarm_sound(level)
    
    def _play_alarm_sound(self, level: int) -> None:
        """
        播放报警声音
        
        Args:
            level: 报警级别
        """
        if not self.sound_player:
            return
        
        try:
            # 获取声音文件路径
            sound_file = self._get_sound_file(level)
            
            # 检查文件是否存在
            if not os.path.exists(sound_file):
                logger.warning(f"声音文件不存在: {sound_file}")
                return
            
            # 加载并播放声音
            sound = self.sound_player.mixer.Sound(sound_file)
            sound.set_volume(self.sound_volume)
            sound.play()
        
        except Exception as e:
            logger.error(f"播放声音失败: {e}")
    
    def _get_sound_file(self, level: int) -> str:
        """
        根据报警级别获取声音文件路径
        
        Args:
            level: 报警级别
            
        Returns:
            str: 声音文件路径
        """
        # 查找声音文件
        base_dir = Path(__file__).parent.parent / "resources" / "sounds"
        
        if level == 3:
            return str(base_dir / "high_alarm.wav")
        elif level == 2:
            return str(base_dir / "medium_alarm.wav")
        else:
            return str(base_dir / "low_alarm.wav")
    
    def save_alarm_image(self, frame: np.ndarray, behavior_type: str) -> Optional[str]:
        """
        保存报警图像
        
        Args:
            frame: 视频帧
            behavior_type: 行为类型
            
        Returns:
            Optional[str]: 保存的图像路径，如果保存失败则为None
        """
        if not self.save_alarm_image:
            return None
        
        try:
            # 检查报警图像数量是否达到上限
            if self.alarm_image_count >= self.max_alarm_images:
                # 删除最旧的图像
                self._remove_oldest_alarm_image()
            
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"alarm_{timestamp}_{behavior_type}.jpg"
            filepath = ALARM_DIR / filename
            
            # 保存图像
            cv2.imwrite(str(filepath), frame)
            self.alarm_image_count += 1
            
            logger.info(f"报警图像已保存: {filepath}")
            return str(filepath)
        
        except Exception as e:
            logger.error(f"保存报警图像失败: {e}")
            return None
    
    def _remove_oldest_alarm_image(self) -> None:
        """删除最旧的报警图像"""
        try:
            image_files = list(ALARM_DIR.glob("alarm_*.jpg"))
            if image_files:
                # 按修改时间排序
                image_files.sort(key=lambda x: os.path.getmtime(x))
                
                # 删除最旧的图像
                os.remove(image_files[0])
                logger.info(f"删除最旧的报警图像: {image_files[0]}")
                self.alarm_image_count -= 1
        
        except Exception as e:
            logger.error(f"删除报警图像失败: {e}")
    
    def get_active_alarm(self) -> Dict[str, Any]:
        """
        获取当前活动的报警信息
        
        Returns:
            Dict[str, Any]: 报警信息
        """
        if not self.is_alarm_active:
            return {"active": False}
        
        # 如果报警已经超过冷却时间，则清除
        if time.time() - self.alarm_start_time > self.alarm_cooldown:
            with self.lock:
                self.is_alarm_active = False
                self.current_alarm_type = None
                return {"active": False}
        
        # 获取报警消息和级别
        message, level = self._get_alarm_info(self.current_alarm_type)
        
        return {
            "active": True,
            "type": self.current_alarm_type,
            "message": message,
            "level": level,
            "start_time": self.alarm_start_time
        }
    
    def clear_alarm(self) -> None:
        """清除当前报警"""
        with self.lock:
            self.is_alarm_active = False
            self.current_alarm_type = None
    
    def shutdown(self) -> None:
        """关闭报警管理器"""
        if self.sound_player:
            try:
                self.sound_player.mixer.quit()
            except:
                pass


# 创建全局实例
alarm_manager = AlarmManager()


if __name__ == "__main__":
    # 测试代码
    import time
    
    # 测试报警管理器
    manager = alarm_manager
    
    # 触发报警
    manager.on_behavior_detected(BehaviorType.EYES_CLOSED, 0.95, {})
    print("触发闭眼报警")
    print(f"当前报警状态: {manager.get_active_alarm()}")
    
    # 等待一会儿
    time.sleep(2)
    
    # 触发另一个报警
    manager.on_behavior_detected(BehaviorType.PHONE_USE, 0.9, {})
    print("触发手机使用报警")
    print(f"当前报警状态: {manager.get_active_alarm()}")
    
    # 等待报警超时
    time.sleep(manager.alarm_cooldown + 1)
    print(f"报警超时后状态: {manager.get_active_alarm()}")
    
    # 测试保存图像
    test_frame = np.ones((480, 640, 3), dtype=np.uint8) * 255
    cv2.putText(test_frame, "TEST ALARM", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    
    image_path = manager.save_alarm_image(test_frame, BehaviorType.DROWSY)
    print(f"保存的报警图像: {image_path}")
    
    # 关闭
    manager.shutdown()
    print("测试完成")
