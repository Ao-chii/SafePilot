# SafePilot API 接口文档

本文档详细描述了 SafePilot 系统的所有 API 接口，供后端开发对接使用。

## 基础信息

- 基础 URL: `/api`
- 所有接口均使用 JSON 格式进行数据交换
- 成功响应状态码为 200，错误响应状态码根据具体错误情况而定

## 1. 用户认证相关接口

### 1.1 用户登录

**接口地址**: `POST /auth/login`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| username | string | 是 | 用户名 |
| password | string | 是 | 密码 |

**响应参数**:

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| access_token | string | 访问令牌 |
| user | object | 用户信息对象 |

**响应示例**:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@safepilot.com",
    "first_name": "管理员",
    "is_admin": true
  }
}
```

### 1.2 用户注册

**接口地址**: `POST /auth/register`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| username | string | 是 | 用户名 |
| email | string | 是 | 邮箱地址 |
| password | string | 是 | 密码 |
| first_name | string | 是 | 姓氏 |
| last_name | string | 否 | 名字 |
| phone | string | 是 | 手机号码 |
| role | string | 是 | 用户角色(driver/admin/supervisor) |

**响应参数**:

| 参数名 | 类型 | 说明 |
| --- | --- | --- |
| user | object | 用户信息对象 |

**响应示例**:

```json
{
  "user": {
    "id": 12,
    "username": "newdriver",
    "email": "driver@example.com",
    "first_name": "张",
    "last_name": "三",
    "phone": "13812345678",
    "role": "driver"
  }
}
```

### 1.3 获取用户资料

**接口地址**: `GET /auth/profile`

**响应参数**:
返回用户详细信息对象。

### 1.4 更新用户资料

**接口地址**: `PUT /auth/profile`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| first_name | string | 否 | 姓氏 |
| last_name | string | 否 | 名字 |
| phone | string | 否 | 手机号码 |

### 1.5 删除账户

**接口地址**: `DELETE /auth/account`

### 1.6 修改密码

**接口地址**: `POST /auth/change-password`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| current_password | string | 是 | 当前密码 |
| new_password | string | 是 | 新密码 |

### 1.7 发送密码重置验证码

**接口地址**: `POST /auth/send-reset-code`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| contact | string | 是 | 联系方式(邮箱或手机号) |
| type | string | 是 | 类型(email/phone) |

### 1.8 验证重置验证码

**接口地址**: `POST /auth/verify-reset-code`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| contact | string | 是 | 联系方式(邮箱或手机号) |
| type | string | 是 | 类型(email/phone) |
| code | string | 是 | 验证码 |

### 1.9 重置密码

**接口地址**: `POST /auth/reset-password`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| contact | string | 是 | 联系方式(邮箱或手机号) |
| type | string | 是 | 类型(email/phone) |
| code | string | 是 | 验证码 |
| new_password | string | 是 | 新密码 |

## 2. 设备管理相关接口

### 2.1 获取设备列表

**接口地址**: `GET /devices`

**响应参数**:
返回设备列表数组。

### 2.2 获取设备详情

**接口地址**: `GET /devices/{device_id}`

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| device_id | string | 是 | 设备ID |

### 2.3 创建设备

**接口地址**: `POST /devices`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| device_id | string | 是 | 设备ID |
| name | string | 是 | 设备名称 |
| description | string | 否 | 设备描述 |
| is_active | boolean | 否 | 是否激活 |

### 2.4 更新设备

**接口地址**: `PUT /devices/{device_id}`

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| device_id | string | 是 | 设备ID |

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| name | string | 否 | 设备名称 |
| description | string | 否 | 设备描述 |
| is_active | boolean | 否 | 是否激活 |

### 2.5 删除设备

**接口地址**: `DELETE /devices/{device_id}`

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| device_id | string | 是 | 设备ID |

## 3. 驾驶员管理相关接口

### 3.1 获取驾驶员列表

**接口地址**: `GET /drivers`

**响应参数**:
返回驾驶员列表数组。

### 3.2 获取驾驶员详情

**接口地址**: `GET /drivers/{driver_id}`

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| driver_id | string | 是 | 驾驶员ID |

### 3.3 创建驾驶员

**接口地址**: `POST /drivers`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| driver_id | string | 是 | 驾驶员ID |
| name | string | 是 | 驾驶员姓名 |

### 3.4 更新驾驶员

**接口地址**: `PUT /drivers/{driver_id}`

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| driver_id | string | 是 | 驾驶员ID |

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| name | string | 否 | 驾驶员姓名 |
| is_active | boolean | 否 | 是否激活 |

### 3.5 删除驾驶员

**接口地址**: `DELETE /drivers/{driver_id}`

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| driver_id | string | 是 | 驾驶员ID |

## 4. 事件数据相关接口

### 4.1 获取事件列表

**接口地址**: `GET /events`

**查询参数**:

| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| device_id | string | 否 | 设备ID |
| driver_id | string | 否 | 驾驶员ID |
| event_type | string | 否 | 事件类型 |
| start_time | string | 否 | 开始时间 |
| end_time | string | 否 | 结束时间 |
| limit | number | 否 | 限制返回数量 |

**响应参数**:
返回事件列表数组。

### 4.2 获取事件详情

**接口地址**: `GET /events/{event_id}`

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| event_id | string | 是 | 事件ID |

### 4.3 创建事件（客户端上报）

**接口地址**: `POST /events`

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| device_id | string | 是 | 设备ID |
| events | array | 是 | 事件数组 |

**events数组元素结构**:

| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| driver_id | string | 是 | 驾驶员ID |
| event_type | string | 是 | 事件类型 |
| confidence | number | 是 | 置信度 |
| timestamp | string | 是 | 时间戳 |
| details | object | 否 | 详细信息 |

## 5. 统计分析相关接口

### 5.1 获取设备统计信息

**接口地址**: `GET /stats/device/{device_id}`

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| device_id | string | 是 | 设备ID |

### 5.2 获取驾驶员统计信息

**接口地址**: `GET /stats/driver/{driver_id}`

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| driver_id | string | 是 | 驾驶员ID |

## 6. 系统相关接口

### 6.1 健康检查

**接口地址**: `GET /system/health`

**响应参数**:
返回系统健康状态信息。

## 7. 实时监控相关接口

### 7.1 获取视频流列表

**接口地址**: `GET /monitor/streams`

**响应参数**:
返回视频流列表数组。

### 7.2 获取指定视频流信息

**接口地址**: `GET /monitor/streams/{stream_id}`

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| stream_id | string | 是 | 视频流ID |

### 7.3 获取实时告警

**接口地址**: `GET /monitor/alerts`

**查询参数**:

| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| limit | number | 否 | 限制返回数量 |
| level | string | 否 | 告警级别 |

**响应参数**:
返回实时告警列表数组。

### 7.4 处理告警

**接口地址**: `POST /monitor/alerts/{alert_id}/handle`

**路径参数**:

| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| alert_id | string | 是 | 告警ID |

**请求参数**:

| 参数名 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| action | string | 是 | 处理动作 |

### 7.5 获取系统状态统计

**接口地址**: `GET /monitor/status`

**响应参数**:
返回系统状态统计信息。