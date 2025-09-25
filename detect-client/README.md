# 驾驶员行为检测与上报系统

一个基于YOLO和MediaPipe的驾驶员行为检测系统，可实时检测危险驾驶行为并上报到服务器。

## 功能特性

- 实时检测驾驶员危险行为（如使用手机、疲劳驾驶、双手脱离方向盘等）
- 实时检测驾驶员警告行为（如饮食、操作娱乐系统等）
- 本地警报提醒（声音报警）
- 事件上报到远程服务器
- 模块化设计，易于扩展和维护
- 可配置的行为检测参数和规则

## 系统架构

```
[视频输入] -> [帧读取模块] -> [YOLO检测模块] -> [MediaPipe分析模块] -> [行为判断引擎] -> [报警与上报模块]
                                                                   -> [UI显示模块 (可选)]
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置说明

配置文件为 `config.yaml`，包含以下主要配置项：

- `camera`: 摄像头设置
- `yolo`: YOLO模型设置
- `mediapipe`: MediaPipe分析设置
- `behavior_rules`: 行为判断规则
- `server`: 服务器上报设置

配置示例：
```yaml
camera:
  source: 0
  width: 640
  height: 480

yolo:
  model_path: "yolo11n.pt"
  confidence_threshold: 0.5
  classes_to_detect: [0, 67, 77]  # 0: person, 67: cell phone, 77: bottle

mediapipe:
  static_image_mode: False
  max_num_faces: 1
  min_detection_confidence: 0.5

behavior_rules:
  eyes_close_threshold: 0.15
  perclos_time_window: 3.0
  perclos_threshold: 0.5
  gaze_off_road_threshold: 2.0
  hands_off_wheel_threshold: 3.0

server:
  api_endpoint: "http://localhost:5000/api/v1/events"
  api_key: "your-api-key-here"
  timeout_seconds: 5
  report_interval: 60  # 同一种行为60秒内只上报一次
```

## 使用方法

```bash
python main.py
```

按 'q' 键退出程序。

## 行为检测说明

### 危险事件 (Danger Events)

1. **使用手机** - YOLO检测到手机物体，MediaPipe Hand检测到手部在手机附近或面部朝向手机
2. **双手脱离方向盘** - MediaPipe Hands检测不到双手在方向盘区域
3. **严重疲劳驾驶** - MediaPipe Face Mesh计算眼睛闭合时间比例(PERCLOS)
4. **视线严重偏离** - MediaPipe Face Mesh估计视线方向
5. **抽烟** - YOLO检测到香烟或烟雾，MediaPipe Hand检测手部动作
6. **转身与后排乘客交流** - MediaPipe Pose估计身体躯干和头部角度

### 警告事件 (Warning Events)

1. **饮食/喝水** - YOLO检测到水瓶、食品包装等物体
2. **操作车载信息娱乐系统** - 手部在中控台屏幕区域持续停留
3. **过度调整车内设备** - 手部在空调旋钮、收音机等位置长时间操作
4. **与乘客过度交谈** - 头部频繁转向副驾驶
5. **轻度疲劳迹象** - 偶尔的哈欠、揉眼睛等
6. **异常头部姿势** - 抓头、托腮等非标准驾驶姿势
7. **未佩戴安全带** - YOLO检测安全带状态
8. **驾驶员不存在** - YOLO在驾驶座上检测不到人

## 模块化架构

系统采用模块化设计，便于扩展和维护：

- `frame_capture.py`: 视频帧捕获模块
- `detector_yolo.py`: YOLO目标检测模块
- `analyzer_mediapipe.py`: MediaPipe分析模块
- `behavior_engine.py`: 行为判断引擎
- `behavior_detectors/`: 具体行为检测器模块
  - `base_detector.py`: 检测器基类
  - `drowsiness_detector.py`: 疲劳检测器
  - `phone_usage_detector.py`: 手机使用检测器
  - `hands_off_wheel_detector.py`: 双手脱离方向盘检测器
- `events.py`: 事件定义模块
- `reporter.py`: 事件上报和报警模块
- `config.py`: 配置管理模块

## 注意事项

- 需要安装摄像头设备
- 需要配置YOLO模型文件（默认使用yolo11n.pt）
- 如需声音报警功能，需要提供alarm.wav文件
- 需要配置服务器API端点以启用事件上报功能
- 可根据实际需求调整行为检测参数

## 系统要求

- Python 3.7+
- 支持CUDA的GPU（推荐，用于提升YOLO检测速度）