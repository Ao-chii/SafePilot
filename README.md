# SafePilot - 驾驶员危险行为检测系统

SafePilot是一个基于计算机视觉的实时驾驶员危险行为检测系统，可以检测包括疲劳驾驶（闭眼、打哈欠）、分心（使用手机、抽烟、喝水）等危险行为，并提供实时声光报警和数据分析功能。系统采用三层架构，包括客户端检测程序、服务器后端和Web管理界面。

## 系统架构

系统采用复合架构风格：
- **三层架构**：表现层、逻辑层和数据层清晰分离
- **客户端-服务器架构**：胖客户端进行实时检测，服务器进行数据管理和分析

### 核心组件

1. **客户端** (`client/`)：
   - 实时视频流采集和处理
   - 基于YOLOv11和MediaPipe的行为检测
   - 本地声光报警
   - 事件数据上报

2. **服务器** (`server/`)：
   - Flask API服务
   - 数据访问层（DAO模式）
   - 用户和设备管理
   - 事件数据存储和统计分析

3. **前端** (`frontend/`)：
   - 基于Vue.js的管理界面
   - 实时数据展示
   - 历史数据查询和分析

## 技术栈

- **计算机视觉**：YOLOv11, MediaPipe, OpenCV
- **后端**：Python, Flask, SQLAlchemy
- **数据库**：SQLite/PostgreSQL
- **前端**：Vue.js, Chart.js

## 安装指南

### 系统要求

- Python 3.8+
- CUDA (可选，用于GPU加速)
- PostgreSQL (可选，默认使用SQLite)

### 安装依赖

1. 客户端依赖：

```bash
pip install -r client_requirements.txt
```

2. 服务器依赖：

```bash
pip install -r server_requirements.txt
```

### 配置

1. 客户端配置：
   - 编辑 `config.json` 配置服务器地址、设备ID等

2. 服务器配置：
   - 编辑 `server_config.json` 配置数据库连接、API参数等

## 使用说明

### 运行客户端

```bash
# 默认使用摄像头
python run_client.py

# 使用指定摄像头
python run_client.py --camera 1

# 使用视频文件
python run_client.py --video path/to/video.mp4

# 指定YOLO模型
python run_client.py --model weights/custom_model.pt

# 启用数据上报
python run_client.py --upload --server http://your_server:5000
```

### 运行服务器

```bash
# 默认配置运行
python run_server.py

# 指定端口
python run_server.py --port 8080

# 使用PostgreSQL
python run_server.py --db postgresql --db-name safepilot --db-user postgres --db-password secret

# 仅初始化数据库
python run_server.py --init-db
```

## 检测功能

系统可以检测以下驾驶员行为：

1. **疲劳状态**：
   - 闭眼（实时跟踪眼睛状态）
   - 打哈欠（检测口部开合度）
   - 基于PERCLOS模型的疲劳评估

2. **分心行为**：
   - 使用手机
   - 抽烟
   - 喝水

3. **注意力跟踪**：
   - 视线跟踪
   - 头部姿态分析

## API文档

服务器提供RESTful API：

- **认证**：`/api/v1/auth/login`, `/api/v1/auth/register`
- **设备管理**：`/api/v1/devices`
- **驾驶员管理**：`/api/v1/drivers`
- **事件数据**：`/api/v1/events`
- **统计分析**：`/api/v1/stats`

详细API文档请参考 `docs/API.md`。

## 系统截图

[这里放置系统运行截图]

## 许可证

本项目采用 MIT 许可证，详情请参阅 LICENSE 文件。

## 致谢

- YOLOv11 by Ultralytics
- MediaPipe by Google
- OpenCV
- Flask