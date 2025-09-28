*   **Danger Events（危险事件）：** 指那些会**立即且直接**导致严重交通事故的行为。这类事件需要系统发出最高优先级的警报，甚至可能触发车辆主动安全系统（如震动方向盘、紧急减速等）。
*   **Warning Events（警告事件）：** 指那些**增加事故风险**的分散注意力或不良驾驶习惯。这类事件需要系统发出提醒，帮助驾驶员纠正行为，培养良好习惯。

---

### 基于YOLO和MediaPipe的可检测行为清单

#### 一、 Danger Events（危险事件）

这类行为是监测系统的核心，要求极高的检测准确率和实时性。

1.  **使用手机**
    *   **检测方法：** YOLO检测到手机物体，MediaPipe Hand检测到手部与头部（通过面部Landmarks确定位置）距离过近，且手部姿态呈握持状。可以进一步区分：
        *   **手持电话通话：** 手机靠近耳朵。
        *   **低头看手机：** 头部明显低下，视线朝向腿部区域（通过头部姿态估计）。

2.  **双手脱离方向盘**
    *   **检测方法：** MediaPipe Hands检测不到双手，或者双手的位置持续一段时间不在方向盘区域（需要预先定义方向盘的大致区域）。

3.  **严重疲劳驾驶**
    *   **检测方法：** MediaPipe Face Mesh用于计算：
        *   **眼睛闭合时间（PERCLOS）：** 单位时间内眼睛闭合的比例，是衡量疲劳的黄金标准。
        *   **频繁、大幅度的点头：** 头部持续低下并突然抬起。
        *   **哈欠频率：** 通过嘴部张开程度和持续时间判断。
    *   **判定：** 当这些指标超过阈值一段时间后，判定为危险事件。

4.  **视线严重偏离（长时间不看路）**
    *   **检测方法：** MediaPipe Face Mesh估计视线方向（Gaze Estimation）。当检测到驾驶员视线偏离前方道路（如看向副驾驶、后座或窗外远处）持续超过2-3秒。

5.  **抽烟**
    *   **检测方法：** YOLO检测到香烟或烟雾，MediaPipe Hand检测到手部有靠近嘴部再放下的重复动作。

6.  **转身与后排乘客交流**
    *   **检测方法：** MediaPipe Pose估计身体躯干和头部的角度。当身体和头部同时大幅度转向后方，并持续一段时间。

#### 二、 Warning Events（警告事件）

这类行为是预防性的，旨在防微杜渐。

1.  **饮食/喝水**
    *   **检测方法：** YOLO检测到水瓶、食品包装等物体。MediaPipe Hand检测到手部有拿起物体送往嘴部的动作。

2.  **操作车载信息娱乐系统**
    *   **检测方法：** 手部在中控台屏幕区域持续停留并有点击动作（虽然难以精确识别点击，但长时间的停留和特定手势可以推断）。

3.  **过度调整车内设备**
    *   **检测方法：** 手部在空调旋钮、收音机等位置长时间操作。

4.  **与乘客过度交谈**
    *   **检测方法：** 头部频繁转向副驾驶，但身体仍基本朝前（与危险事件中的“转身”区别开）。可以结合面部Landmarks检测是否在说话（嘴部活动频繁）。

5.  **轻度疲劳迹象**
    *   **检测方法：** 同危险事件中的疲劳检测，但指标较轻或持续时间较短，例如偶尔的哈欠、揉眼睛（MediaPipe Hand检测到手部与眼部接触）。

6.  **异常头部姿势（如抓头、托腮）**
    *   **检测方法：** MediaPipe Pose/Hands检测到非标准驾驶姿势，如单手或双手长时间离开方向盘区域但并未进行明确的其他危险行为（如玩手机）。

7.  **未佩戴安全带**
    *   **检测方法：** YOLO可以直接检测安全带是否佩戴。或者通过MediaPipe Pose估计的肩膀关键点与一条带状区域（安全带区域）的相对位置关系进行判断。

8.  **驾驶员不存在（用于自动驾驶接管提醒）**
    *   **检测方法：** YOLO在驾驶座上检测不到人。这在高级别自动驾驶中，用于提醒驾驶员需要接管车辆。

---

### 技术实现思路

1.  **YOLO的角色：**
    *   **物体检测：** 检测手机、香烟、水瓶、食品等危险相关物体。
    *   **驾驶员检测：** 确保监测区域存在驾驶员，并定位驾驶员的大致区域，作为MediaPipe分析的ROI（Region of Interest）。

2.  **MediaPipe的角色：**
    *   **Face Mesh：** 核心模块。用于疲劳检测（眼、嘴）、视线估计、头部姿态估计。
    *   **Hands：** 核心模块。用于检测手部位置、姿态、轨迹，判断是否握持物体、接触面部等。
    *   **Pose：** 用于检测身体姿态，判断是否转身、弯腰等。

3.  **系统工作流：**
    *   **步骤1：** YOLO处理视频帧，定位驾驶员和车内相关物体（手机、水杯等）。
    *   **步骤2：** 将驾驶员区域传递给MediaPipe的Face、Hands、Pose模型，获取详细的关键点信息。
    *   **步骤3：** **定义业务逻辑规则**。这是项目的精髓，将关键点信息转化为具体行为判断。
        *   **例如判断“看手机”：** `IF (YOLO检测到手机) AND (Hands检测到手靠近手机) AND (Face检测到头部低下且视线朝向手部) THEN Event = 危险事件(使用手机)`
        *   **例如判断“疲劳”：** `IF (Face计算出的PERCLOS值 > 0.8 持续3秒) OR (单位时间内打哈欠次数 > 3) THEN Event = 危险事件(严重疲劳)`
    *   **步骤4：** 根据事件的分类（Danger/Warning），触发不同级别的报警机制。

### 注意事项与挑战

*   **光照条件：** 夜晚、隧道进出等光线剧烈变化会严重影响检测效果，可能需要红外摄像头。
*   **遮挡：** 帽子、墨镜、口罩等会遮挡面部关键点，需要算法有一定的鲁棒性。
*   **个体差异：** 不同人的驾驶习惯、面部特征不同，阈值可能需要自适应调整。
*   **误报与漏报的平衡：** 过于敏感会导致误报频繁，影响体验；过于宽松则会漏报，失去意义。需要在真实场景中大量测试和调优。


好的，基于我们之前讨论的需求，我将为您设计一个可扩展、模块化的Python程序架构。这个架构将整合YOLO和MediaPipe，并实现危险事件的实时上报。

### 系统架构设计

本系统采用**模块化管道架构**，每个模块负责一个特定任务，数据像水流一样在管道中传递。这种设计便于调试、维护和功能扩展。

以下是核心架构图：

```
[视频输入] -> [帧读取模块] -> [YOLO检测模块] -> [MediaPipe分析模块] -> [行为判断引擎] -> [报警与上报模块]
                                                                   -> [UI显示模块 (可选)]
```

---

### 核心模块详细设计

#### 1. 配置管理器 (`config.py`)
使用配置文件（如YAML或JSON）来管理所有可调参数，避免硬编码。
```yaml
# config.yaml
camera:
  source: 0  # 0 为默认摄像头，也可以是视频文件路径或RTSP流
  width: 640
  height: 480

yolo:
  model_path: "models/yolov8n.pt"  # 或您训练的模型
  confidence_threshold: 0.5
  classes_to_detect: [0, 67, 77]  # 0: person, 67: cell phone, 77: bottle (COCO数据集类别)

mediapipe:
  static_image_mode: False
  max_num_faces: 1
  min_detection_confidence: 0.5

behavior_rules:
  eyes_close_threshold: 0.25  # 眼睛长宽比阈值，小于此值视为闭合
  perclos_time_window: 3.0    # 计算PERCLOS的时间窗口（秒）
  perclos_threshold: 0.8      # PERCLOS阈值，超过即为疲劳
  gaze_off_road_threshold: 2.0 # 视线偏离道路的时间阈值（秒）

server:
  api_endpoint: "https://your-server.com/api/event"
  api_key: "your-api-key-here"
  timeout_seconds: 5
```

#### 2. 帧读取模块 (`frame_capture.py`)
负责从摄像头、视频文件或网络流中稳定地读取帧。
```python
import cv2
from queue import Queue
import threading

class FrameCapture:
    def __init__(self, source, frame_queue_maxsize=64):
        self.cap = cv2.VideoCapture(source)
        self.frame_queue = Queue(maxsize=frame_queue_maxsize)
        self.running = True
        # 使用单独的线程读取帧，避免I/O阻塞主流程
        self.thread = threading.Thread(target=self._update_frame, daemon=True)
        self.thread.start()

    def _update_frame(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                break
            if not self.frame_queue.full():
                # 如果队列满了，丢弃旧帧，放入新帧
                if self.frame_queue.full():
                    try:
                        self.frame_queue.get_nowait()
                    except:
                        pass
                self.frame_queue.put(frame)

    def get_frame(self):
        try:
            return self.frame_queue.get(timeout=1.0)
        except:
            return None

    def release(self):
        self.running = False
        self.thread.join()
        self.cap.release()
```

#### 3. YOLO检测模块 (`detector_yolo.py`)
封装YOLO模型，负责检测驾驶员和危险物品。
```python
from ultralytics import YOLO
import cv2

class YOLODetector:
    def __init__(self, model_path, conf_threshold, classes):
        self.model = YOLO(model_path)
        self.conf_threshold = conf_threshold
        self.classes = classes

    def detect(self, frame):
        results = self.model(frame, verbose=False, conf=self.conf_threshold, classes=self.classes)
        # 简化处理：只取第一个结果（假设场景中只有一个主要对象）
        result = results[0] if len(results) > 0 else None
        detections = []
        if result and result.boxes is not None:
            for box in result.boxes:
                xyxy = box.xyxy[0].cpu().numpy().astype(int) # 边框坐标 [x1, y1, x2, y2]
                conf = box.conf[0].cpu().numpy()             # 置信度
                cls_id = int(box.cls[0].cpu().numpy())       # 类别ID
                detections.append({
                    'class_id': cls_id,
                    'class_name': result.names[cls_id],
                    'confidence': conf,
                    'bbox': xyxy
                })
        return detections, result.plot() # 返回检测结果和绘制了框的图像（用于UI）
```

#### 4. MediaPipe分析模块 (`analyzer_mediapipe.py`)
封装MediaPipe，提取驾驶员的面部、手部和姿态关键点。
```python
import mediapipe as mp
import cv2
import numpy as np

class MediaPipeAnalyzer:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_hands = mp.solutions.hands
        self.mp_pose = mp.solutions.pose

        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True, # 启用眼球和嘴唇精细 landmarks
            min_detection_confidence=0.5
        )
        self.hands = self.mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5)
        self.pose = self.mp_pose.Pose(static_image_mode=False, model_complexity=1, min_detection_confidence=0.5)

    def analyze(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = {}
        
        # 1. 面部网格分析 (用于疲劳、视线)
        results['face'] = self.face_mesh.process(rgb_frame)
        # 2. 手部分析
        results['hands'] = self.hands.process(rgb_frame)
        # 3. 姿态分析
        results['pose'] = self.pose.process(rgb_frame)

        return results

    def calculate_eye_aspect_ratio(self, eye_landmarks):
        # 计算眼睛长宽比(EAR)的辅助函数
        # 需要根据面部landmarks的索引获取眼睛周围的关键点
        # 实现细节略...
        pass

    def estimate_gaze_direction(self, face_landmarks, frame_shape):
        # 估算视线方向的辅助函数
        # 实现细节略...
        pass
```

#### 5. 行为判断引擎 (`behavior_engine.py`)
**这是系统的核心逻辑**，它接收YOLO和MediaPipe的结果，根据预定义的规则判断行为。
```python
import time
from collections import deque
from enum import Enum

class EventType(Enum):
    DANGER = "DANGER"
    WARNING = "WARNING"

class DangerousBehavior(Enum):
    PHONE_CALL = 1
    PHONE_READING = 2
    HANDS_OFF_WHEEL = 3
    SEVERE_DROWSINESS = 4
    GAZE_OFF_ROAD = 5
    SMOKING = 6
    TURNING_AROUND = 7

class BehaviorEngine:
    def __init__(self, config):
        self.config = config
        # 用于状态跟踪的变量
        self.eye_close_deque = deque(maxlen=30) # 记录最近30帧的眼睛状态
        self.last_eyes_open_time = time.time()
        self.gaze_off_road_start_time = None
        self.hands_last_seen_on_wheel = time.time()

    def process(self, yolo_detections, mediapipe_results, frame):
        """主处理函数，返回检测到的事件列表"""
        events = []

        # 规则1： 使用手机检测
        phone_detected = any(det['class_name'] == 'cell phone' for det in yolo_detections)
        if phone_detected and mediapipe_results['hands'].multi_hand_landmarks:
            # 简化的逻辑：如果检测到手机且有手部动作，则判断为危险
            # 更精确的逻辑需要判断手和手机的相对位置、头部姿态等
            events.append({
                'type': EventType.DANGER,
                'behavior': DangerousBehavior.PHONE_READING,
                'confidence': 0.9, # 可以根据重叠度等计算
                'timestamp': time.time()
            })

        # 规则2： 疲劳检测 (PERCLOS)
        if mediapipe_results['face'].multi_face_landmarks:
            face_landmarks = mediapipe_results['face'].multi_face_landmarks[0]
            left_eye_ear = self.calculate_eye_aspect_ratio(face_landmarks, 'left')
            right_eye_ear = self.calculate_eye_aspect_ratio(face_landmarks, 'right')
            avg_ear = (left_eye_ear + right_eye_ear) / 2.0

            is_eyes_closed = avg_ear < self.config['behavior_rules']['eyes_close_threshold']
            self.eye_close_deque.append(is_eyes_closed)

            # 计算过去N秒内眼睛闭合的帧所占的比例 (PERCLOS)
            time_window_frames = int(self.config['behavior_rules']['perclos_time_window'] * 30) # 假设30fps
            recent_deque = list(self.eye_close_deque)[-time_window_frames:]
            if len(recent_deque) > 0:
                perclos = sum(recent_deque) / len(recent_deque)
                if perclos > self.config['behavior_rules']['perclos_threshold']:
                    events.append({
                        'type': EventType.DANGER,
                        'behavior': DangerousBehavior.SEVERE_DROWSINESS,
                        'confidence': perclos,
                        'timestamp': time.time()
                    })

        # 规则3： 双手脱离方向盘检测
        # 假设方向盘在图像底部中央区域
        wheel_region = [frame.shape[1]//4, 3*frame.shape[0]//4, frame.shape[1]//2, frame.shape[0]//4]
        hands_on_wheel = self._check_hands_in_region(mediapipe_results, wheel_region)
        if not hands_on_wheel:
            time_off = time.time() - self.hands_last_seen_on_wheel
            if time_off > 3.0: # 持续3秒无手
                events.append({
                    'type': EventType.DANGER,
                    'behavior': DangerousBehavior.HANDS_OFF_WHEEL,
                    'confidence': 0.8,
                    'timestamp': time.time()
                })
        else:
            self.hands_last_seen_on_wheel = time.time()

        # ... 实现其他规则（视线偏离、抽烟等）

        return events

    def _check_hands_in_region(self, mediapipe_results, region):
        # 检查手部关键点是否在方向盘区域内
        # 实现细节略...
        pass
```

#### 6. 报警与上报模块 (`reporter.py`)
负责管理警报（声音、UI提示）和向服务器上报危险事件。
```python
import requests
import json
import threading
from playsound import playsound # 用于播放警报音

class Reporter:
    def __init__(self, config):
        self.config = config['server']
        self.last_report_time = {} # 记录上次上报每种行为的时间，防止频繁上报

    def handle_events(self, events):
        for event in events:
            print(f"[{event['type'].value}] {event['behavior'].name} (Confidence: {event['confidence']:.2f})")
            
            # 如果是危险事件，立即触发警报和上报
            if event['type'] == EventType.DANGER:
                # 1. 播放警报音（在非阻塞线程中）
                threading.Thread(target=self._play_alarm, daemon=True).start()
                # 2. 上报服务器（在非阻塞线程中）
                threading.Thread(target=self._report_to_server, args=(event,), daemon=True).start()

            # 如果是警告事件，可以只做UI提示或记录日志
            elif event['type'] == EventType.WARNING:
                # 例如在图像上绘制警告文本
                pass

    def _play_alarm(self):
        try:
            playsound("alarm.wav")
        except:
            print("Could not play alarm sound.")

    def _report_to_server(self, event):
        # 防频繁上报：例如，同一种行为60秒内只上报一次
        behavior_key = event['behavior'].name
        current_time = time.time()
        if behavior_key in self.last_report_time:
            if current_time - self.last_report_time[behavior_key] < 60:
                return

        payload = {
            "event_type": event['type'].value,
            "behavior": event['behavior'].name,
            "confidence": event['confidence'],
            "timestamp": event['timestamp'],
            "vehicle_id": "XYZ-001" # 应从配置或CAN总线获取
        }

        headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.config['api_key']
        }

        try:
            response = requests.post(
                self.config['api_endpoint'],
                data=json.dumps(payload),
                headers=headers,
                timeout=self.config['timeout_seconds']
            )
            if response.status_code == 200:
                print(f"Successfully reported {behavior_key} to server.")
                self.last_report_time[behavior_key] = current_time
            else:
                print(f"Failed to report {behavior_key}. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error reporting to server: {e}")
```

#### 7. 主程序 (`main.py`)
将所有模块串联起来，形成完整的工作流。
```python
import cv2
import time
import yaml
from frame_capture import FrameCapture
from detector_yolo import YOLODetector
from analyzer_mediapipe import MediaPipeAnalyzer
from behavior_engine import BehaviorEngine
from reporter import Reporter

def main():
    # 1. 加载配置
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    # 2. 初始化各个模块
    frame_capture = FrameCapture(config['camera']['source'])
    yolo_detector = YOLODetector(config['yolo']['model_path'], config['yolo']['confidence_threshold'], config['yolo']['classes_to_detect'])
    mp_analyzer = MediaPipeAnalyzer()
    behavior_engine = BehaviorEngine(config)
    reporter = Reporter(config)

    print("Driver Monitoring System Started. Press 'q' to quit.")

    try:
        while True:
            # 3. 获取一帧图像
            frame = frame_capture.get_frame()
            if frame is None:
                break

            # 4. YOLO检测
            yolo_detections, annotated_frame = yolo_detector.detect(frame)

            # 5. MediaPipe分析
            mp_results = mp_analyzer.analyze(frame)

            # 6. 行为判断
            events = behavior_engine.process(yolo_detections, mp_results, frame)

            # 7. 处理事件（报警和上报）
            if events:
                reporter.handle_events(events)

            # 8. (可选) 显示结果
            cv2.imshow('Driver Monitoring', annotated_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            # 控制处理频率，避免过高CPU占用
            time.sleep(0.03) # ~30 FPS

    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        # 9. 清理资源
        frame_capture.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
```

### 部署与运行建议

1.  **环境搭建：** 使用Conda或Docker创建独立的Python环境，安装PyTorch (for YOLO), OpenCV, MediaPipe, Ultralytics等依赖。
2.  **硬件选择：** 推荐使用带GPU的机器（如NVIDIA Jetson Nano/NX用于嵌入式部署，或带显卡的PC）以提升YOLO的处理速度。
3.  **模型优化：** 为实时性考虑，使用轻量级模型（如YOLOv8n, YOLOv8s）。可以考虑使用TensorRT进一步加速。
4.  **服务端API：** 您需要提前准备好一个可以接收POST请求的服务器端点，用于处理上报的事件数据。  