# SafePilot 数据库设计文档

本文档详细描述了 SafePilot 系统的数据库设计，包括各数据表的结构和关系。

## 1. 数据库概览

系统采用关系型数据库设计，主要包含用户认证、设备管理、驾驶员管理、事件数据、统计分析和监控等模块。

## 2. 用户相关表

### 2.1 users 表（用户表）

存储系统所有用户的信息，包括管理员、驾驶员和监管员。

| 字段名 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | BIGINT | PRIMARY KEY, AUTO_INCREMENT | 用户ID |
| username | VARCHAR(50) | UNIQUE, NOT NULL | 用户名 |
| email | VARCHAR(100) | UNIQUE, NOT NULL | 邮箱地址 |
| password_hash | VARCHAR(255) | NOT NULL | 密码哈希值 |
| first_name | VARCHAR(50) | NOT NULL | 姓氏 |
| last_name | VARCHAR(50) |  | 名字 |
| phone | VARCHAR(20) | NOT NULL | 手机号码 |
| role | ENUM('driver', 'admin', 'supervisor') | NOT NULL | 用户角色 |
| is_active | BOOLEAN | DEFAULT TRUE | 账户是否激活 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间 |

### 2.2 password_reset_codes 表（密码重置验证码表）

存储用户密码重置的验证码信息。

| 字段名 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | BIGINT | PRIMARY KEY, AUTO_INCREMENT | ID |
| contact | VARCHAR(100) | NOT NULL | 联系方式(邮箱或手机号) |
| code | VARCHAR(10) | NOT NULL | 验证码 |
| type | ENUM('email', 'phone') | NOT NULL | 类型 |
| expires_at | TIMESTAMP | NOT NULL | 过期时间 |
| used | BOOLEAN | DEFAULT FALSE | 是否已使用 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

## 3. 设备相关表

### 3.1 devices 表（设备表）

存储所有设备的信息。

| 字段名 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | VARCHAR(50) | PRIMARY KEY | 设备ID |
| name | VARCHAR(100) | NOT NULL | 设备名称 |
| description | TEXT |  | 设备描述 |
| is_active | BOOLEAN | DEFAULT TRUE | 是否激活 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间 |

## 4. 驾驶员相关表

### 4.1 drivers 表（驾驶员表）

存储驾驶员信息。

| 字段名 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | VARCHAR(50) | PRIMARY KEY | 驾驶员ID |
| name | VARCHAR(100) | NOT NULL | 驾驶员姓名 |
| is_active | BOOLEAN | DEFAULT TRUE | 是否激活 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间 |

## 5. 事件数据相关表

### 5.1 events 表（事件表）

存储系统检测到的所有事件。

| 字段名 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | BIGINT | PRIMARY KEY, AUTO_INCREMENT | 事件ID |
| device_id | VARCHAR(50) | FOREIGN KEY (devices.id) | 设备ID |
| driver_id | VARCHAR(50) | FOREIGN KEY (drivers.id) | 驾驶员ID |
| event_type | VARCHAR(50) | NOT NULL | 事件类型 |
| confidence | DECIMAL(3,2) | NOT NULL | 置信度(0-1) |
| timestamp | TIMESTAMP | NOT NULL | 时间戳 |
| details | JSON |  | 详细信息 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

## 6. 统计分析相关表

### 6.1 device_stats 表（设备统计数据表）

存储设备的统计信息。

| 字段名 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | BIGINT | PRIMARY KEY, AUTO_INCREMENT | ID |
| device_id | VARCHAR(50) | FOREIGN KEY (devices.id) | 设备ID |
| stat_type | VARCHAR(50) | NOT NULL | 统计类型 |
| stat_value | JSON | NOT NULL | 统计值 |
| recorded_at | TIMESTAMP | NOT NULL | 记录时间 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

### 6.2 driver_stats 表（驾驶员统计数据表）

存储驾驶员的统计信息。

| 字段名 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | BIGINT | PRIMARY KEY, AUTO_INCREMENT | ID |
| driver_id | VARCHAR(50) | FOREIGN KEY (drivers.id) | 驾驶员ID |
| stat_type | VARCHAR(50) | NOT NULL | 统计类型 |
| stat_value | JSON | NOT NULL | 统计值 |
| recorded_at | TIMESTAMP | NOT NULL | 记录时间 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

## 7. 监控相关表

### 7.1 video_streams 表（视频流表）

存储视频流信息。

| 字段名 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | VARCHAR(50) | PRIMARY KEY | 视频流ID |
| device_id | VARCHAR(50) | FOREIGN KEY (devices.id) | 关联设备ID |
| name | VARCHAR(100) | NOT NULL | 流名称 |
| url | VARCHAR(255) | NOT NULL | 流地址 |
| is_active | BOOLEAN | DEFAULT TRUE | 是否激活 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 更新时间 |

### 7.2 alerts 表（告警表）

存储系统告警信息。

| 字段名 | 类型 | 约束 | 说明 |
| --- | --- | --- | --- |
| id | VARCHAR(50) | PRIMARY KEY | 告警ID |
| device_id | VARCHAR(50) | FOREIGN KEY (devices.id) | 关联设备ID |
| alert_level | ENUM('low', 'medium', 'high', 'critical') | NOT NULL | 告警级别 |
| alert_type | VARCHAR(50) | NOT NULL | 告警类型 |
| message | TEXT | NOT NULL | 告警消息 |
| details | JSON |  | 详细信息 |
| handled | BOOLEAN | DEFAULT FALSE | 是否已处理 |
| handled_by | BIGINT | FOREIGN KEY (users.id) | 处理人 |
| handled_at | TIMESTAMP |  | 处理时间 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

## 8. 索引设计

为了提高查询性能，需要在以下字段上创建索引：

1. users表: username, email, role
2. events表: device_id, driver_id, event_type, timestamp
3. alerts表: device_id, alert_level, created_at, handled
4. video_streams表: device_id, is_active
5. device_stats表: device_id, stat_type, recorded_at
6. driver_stats表: driver_id, stat_type, recorded_at

## 9. 关系图

以下ER图展示了数据库中各个表之间的关系：

``` mermaid
erDiagram
    users ||--o{ alerts : handles
    users ||--o{ password_reset_codes : "has"
    devices ||--o{ events : "generates"
    devices ||--o{ video_streams : "has"
    devices ||--o{ alerts : "triggers"
    devices ||--o{ device_stats : "has"
    drivers ||--o{ events : "involved in"
    drivers ||--o{ driver_stats : "has"

    users {
        BIGINT id PK
        VARCHAR(50) username
        VARCHAR(100) email
        VARCHAR(255) password_hash
        VARCHAR(50) first_name
        VARCHAR(50) last_name
        VARCHAR(20) phone
        ENUM role
        BOOLEAN is_active
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }

    password_reset_codes {
        BIGINT id PK
        VARCHAR(100) contact
        VARCHAR(10) code
        ENUM type
        TIMESTAMP expires_at
        BOOLEAN used
        TIMESTAMP created_at
    }

    devices {
        VARCHAR(50) id PK
        VARCHAR(100) name
        TEXT description
        BOOLEAN is_active
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }

    drivers {
        VARCHAR(50) id PK
        VARCHAR(100) name
        BOOLEAN is_active
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }

    events {
        BIGINT id PK
        VARCHAR(50) device_id FK
        VARCHAR(50) driver_id FK
        VARCHAR(50) event_type
        DECIMAL(3,2) confidence
        TIMESTAMP timestamp
        JSON details
        TIMESTAMP created_at
    }

    device_stats {
        BIGINT id PK
        VARCHAR(50) device_id FK
        VARCHAR(50) stat_type
        JSON stat_value
        TIMESTAMP recorded_at
        TIMESTAMP created_at
    }

    driver_stats {
        BIGINT id PK
        VARCHAR(50) driver_id FK
        VARCHAR(50) stat_type
        JSON stat_value
        TIMESTAMP recorded_at
        TIMESTAMP created_at
    }

    video_streams {
        VARCHAR(50) id PK
        VARCHAR(50) device_id FK
        VARCHAR(100) name
        VARCHAR(255) url
        BOOLEAN is_active
        TIMESTAMP created_at
        TIMESTAMP updated_at
    }

    alerts {
        VARCHAR(50) id PK
        VARCHAR(50) device_id FK
        ENUM alert_level
        VARCHAR(50) alert_type
        TEXT message
        JSON details
        BOOLEAN handled
        BIGINT handled_by FK
        TIMESTAMP handled_at
        TIMESTAMP created_at
    }
```

图中展示了以下关键关系：
1. 一个用户可以处理多个告警，一个告警只能被一个用户处理
2. 一个用户可以有多个密码重置码记录
3. 一个设备可以产生多个事件，一个事件只属于一个设备
4. 一个设备可以有多个视频流，一个视频流只属于一个设备
5. 一个设备可以触发多个告警，一个告警只属于一个设备
6. 一个设备可以有多个统计数据记录
7. 一个驾驶员可以涉及多个事件，一个事件只涉及一个驾驶员
8. 一个驾驶员可以有多个统计数据记录
