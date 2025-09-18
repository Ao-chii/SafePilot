# API 模块

import json
import datetime
import logging
from typing import Dict, Any, List, Optional, Union, Tuple

from flask import Flask, request, jsonify, g
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity, verify_jwt_in_request
)
from werkzeug.security import generate_password_hash, check_password_hash

from server.config import config
from server.models import (
    init_db, user_dao, device_dao, driver_dao, event_dao,
    User, Device, Driver, Event
)

logger = logging.getLogger("SafePilotServer.API")

# 创建Flask应用
app = Flask(__name__)

# 从配置加载
app.config["SECRET_KEY"] = config.secret_key
app.config["JWT_SECRET_KEY"] = config.jwt_secret_key
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(seconds=config.jwt_access_token_expires)
app.config["DEBUG"] = config.debug

# 初始化JWT
jwt = JWTManager(app)

# 初始化CORS
CORS(app, resources={f"{config.api_prefix}/*": {"origins": config.cors_origins}})

# API前缀
API_PREFIX = f"{config.api_prefix}/{config.api_version}"


# 身份验证相关API
@app.route(f"{API_PREFIX}/auth/login", methods=["POST"])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "无效的请求数据"}), 400
        
        username = data.get("username")
        password = data.get("password")
        
        if not username or not password:
            return jsonify({"error": "用户名和密码不能为空"}), 400
        
        # 检查用户是否存在
        user = user_dao.get_by_username(username)
        if not user:
            return jsonify({"error": "用户不存在"}), 404
        
        # 检查密码
        if not check_password_hash(user.password_hash, password):
            return jsonify({"error": "密码错误"}), 401
        
        # 检查用户状态
        if not user.is_active:
            return jsonify({"error": "用户已停用"}), 403
        
        # 创建访问令牌
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            "access_token": access_token,
            "user": user.to_dict()
        })
    
    except Exception as e:
        logger.error(f"登录错误: {e}")
        return jsonify({"error": "服务器内部错误"}), 500


@app.route(f"{API_PREFIX}/auth/register", methods=["POST"])
def register():
    """用户注册"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "无效的请求数据"}), 400
        
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        
        if not username or not email or not password:
            return jsonify({"error": "用户名、邮箱和密码不能为空"}), 400
        
        # 检查用户名是否已存在
        if user_dao.get_by_username(username):
            return jsonify({"error": "用户名已存在"}), 409
        
        # 检查邮箱是否已存在
        if user_dao.get_by_email(email):
            return jsonify({"error": "邮箱已存在"}), 409
        
        # 创建用户
        password_hash = generate_password_hash(password)
        user = user_dao.create(
            username=username,
            email=email,
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name
        )
        
        # 创建访问令牌
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            "access_token": access_token,
            "user": user.to_dict()
        }), 201
    
    except Exception as e:
        logger.error(f"注册错误: {e}")
        return jsonify({"error": "服务器内部错误"}), 500


@app.route(f"{API_PREFIX}/auth/profile", methods=["GET"])
@jwt_required()
def get_profile():
    """获取用户资料"""
    try:
        # 获取当前用户ID
        user_id = get_jwt_identity()
        
        # 获取用户信息
        user = user_dao.get_by_id(user_id)
        if not user:
            return jsonify({"error": "用户不存在"}), 404
        
        return jsonify({"user": user.to_dict()})
    
    except Exception as e:
        logger.error(f"获取用户资料错误: {e}")
        return jsonify({"error": "服务器内部错误"}), 500


@app.route(f"{API_PREFIX}/auth/change-password", methods=["POST"])
@jwt_required()
def change_password():
    """修改密码"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "无效的请求数据"}), 400
        
        old_password = data.get("old_password")
        new_password = data.get("new_password")
        
        if not old_password or not new_password:
            return jsonify({"error": "旧密码和新密码不能为空"}), 400
        
        # 获取当前用户
        user_id = get_jwt_identity()
        user = user_dao.get_by_id(user_id)
        if not user:
            return jsonify({"error": "用户不存在"}), 404
        
        # 检查旧密码
        if not check_password_hash(user.password_hash, old_password):
            return jsonify({"error": "旧密码错误"}), 401
        
        # 更新密码
        password_hash = generate_password_hash(new_password)
        user_dao.update(user.id, password_hash=password_hash)
        
        return jsonify({"message": "密码修改成功"})
    
    except Exception as e:
        logger.error(f"修改密码错误: {e}")
        return jsonify({"error": "服务器内部错误"}), 500


# 设备相关API
@app.route(f"{API_PREFIX}/devices", methods=["GET"])
@jwt_required()
def get_devices():
    """获取设备列表"""
    try:
        # 获取当前用户ID
        user_id = get_jwt_identity()
        
        # 获取设备列表
        devices = device_dao.get_by_owner_id(user_id)
        
        # 转换为字典列表
        result = [device.to_dict() for device in devices]
        
        return jsonify({"devices": result})
    
    except Exception as e:
        logger.error(f"获取设备列表错误: {e}")
        return jsonify({"error": "服务器内部错误"}), 500


@app.route(f"{API_PREFIX}/devices/<string:device_id>", methods=["GET"])
@jwt_required()
def get_device(device_id):
    """获取设备详情"""
    try:
        # 获取当前用户ID
        user_id = get_jwt_identity()
        
        # 获取设备
        device = device_dao.get_by_device_id(device_id)
        if not device:
            return jsonify({"error": "设备不存在"}), 404
        
        # 检查权限
        if device.owner_id != user_id:
            return jsonify({"error": "无权访问该设备"}), 403
        
        return jsonify({"device": device.to_dict()})
    
    except Exception as e:
        logger.error(f"获取设备详情错误: {e}")
        return jsonify({"error": "服务器内部错误"}), 500


@app.route(f"{API_PREFIX}/devices", methods=["POST"])
@jwt_required()
def create_device():
    """创建设备"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "无效的请求数据"}), 400
        
        device_id = data.get("device_id")
        name = data.get("name")
        description = data.get("description", "")
        
        if not device_id or not name:
            return jsonify({"error": "设备ID和名称不能为空"}), 400
        
        # 检查设备ID是否已存在
        if device_dao.get_by_device_id(device_id):
            return jsonify({"error": "设备ID已存在"}), 409
        
        # 获取当前用户ID
        user_id = get_jwt_identity()
        
        # 创建设备
        device = device_dao.create(
            device_id=device_id,
            name=name,
            description=description,
            owner_id=user_id
        )
        
        return jsonify({"device": device.to_dict()}), 201
    
    except Exception as e:
        logger.error(f"创建设备错误: {e}")
        return jsonify({"error": "服务器内部错误"}), 500


@app.route(f"{API_PREFIX}/devices/<string:device_id>", methods=["PUT"])
@jwt_required()
def update_device(device_id):
    """更新设备"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "无效的请求数据"}), 400
        
        # 获取当前用户ID
        user_id = get_jwt_identity()
        
        # 获取设备
        device = device_dao.get_by_device_id(device_id)
        if not device:
            return jsonify({"error": "设备不存在"}), 404
        
        # 检查权限
        if device.owner_id != user_id:
            return jsonify({"error": "无权修改该设备"}), 403
        
        # 更新设备
        name = data.get("name")
        description = data.get("description")
        is_active = data.get("is_active")
        
        update_data = {}
        if name is not None:
            update_data["name"] = name
        if description is not None:
            update_data["description"] = description
        if is_active is not None:
            update_data["is_active"] = is_active
        
        if update_data:
            device = device_dao.update(device.id, **update_data)
        
        return jsonify({"device": device.to_dict()})
    
    except Exception as e:
        logger.error(f"更新设备错误: {e}")
        return jsonify({"error": "服务器内部错误"}), 500


@app.route(f"{API_PREFIX}/devices/<string:device_id>", methods=["DELETE"])
@jwt_required()
def delete_device(device_id):
    """删除设备"""
    try:
        # 获取当前用户ID
        user_id = get_jwt_identity()
        
        # 获取设备
        device = device_dao.get_by_device_id(device_id)
        if not device:
            return jsonify({"error": "设备不存在"}), 404
        
        # 检查权限
        if device.owner_id != user_id:
            return jsonify({"error": "无权删除该设备"}), 403
        
        # 删除设备
        device_dao.delete(device.id)
        
        return jsonify({"message": "设备已删除"})
    
    except Exception as e:
        logger.error(f"删除设备错误: {e}")
        return jsonify({"error": "服务器内部错误"}), 500


# 驾驶员相关API
@app.route(f"{API_PREFIX}/drivers", methods=["GET"])
@jwt_required()
def get_drivers():
    """获取驾驶员列表"""
    try:
        # 获取当前用户ID
        user_id = get_jwt_identity()
        
        # 获取驾驶员列表
        drivers = driver_dao.get_by_owner_id(user_id)
        
        # 转换为字典列表
        result = [driver.to_dict() for driver in drivers]
        
        return jsonify({"drivers": result})
    
    except Exception as e:
        logger.error(f"获取驾驶员列表错误: {e}")
        return jsonify({"error": "服务器内部错误"}), 500


@app.route(f"{API_PREFIX}/drivers/<string:driver_id>", methods=["GET"])
@jwt_required()
def get_driver(driver_id):
    """获取驾驶员详情"""
    try:
        # 获取当前用户ID
        user_id = get_jwt_identity()
        
        # 获取驾驶员
        driver = driver_dao.get_by_driver_id(driver_id)
        if not driver:
            return jsonify({"error": "驾驶员不存在"}), 404
        
        # 检查权限
        if driver.owner_id != user_id:
            return jsonify({"error": "无权访问该驾驶员"}), 403
        
        return jsonify({"driver": driver.to_dict()})
    
    except Exception as e:
        logger.error(f"获取驾驶员详情错误: {e}")
        return jsonify({"error": "服务器内部错误"}), 500


@app.route(f"{API_PREFIX}/drivers", methods=["POST"])
@jwt_required()
def create_driver():
    """创建驾驶员"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "无效的请求数据"}), 400
        
        driver_id = data.get("driver_id")
        name = data.get("name")
        
        if not driver_id or not name:
            return jsonify({"error": "驾驶员ID和姓名不能为空"}), 400
        
        # 检查驾驶员ID是否已存在
        if driver_dao.get_by_driver_id(driver_id):
            return jsonify({"error": "驾驶员ID已存在"}), 409
        
        # 获取当前用户ID
        user_id = get_jwt_identity()
        
        # 创建驾驶员
        driver = driver_dao.create(
            driver_id=driver_id,
            name=name,
            owner_id=user_id
        )
        
        return jsonify({"driver": driver.to_dict()}), 201
    
    except Exception as e:
        logger.error(f"创建驾驶员错误: {e}")
        return jsonify({"error": "服务器内部错误"}), 500


@app.route(f"{API_PREFIX}/drivers/<string:driver_id>", methods=["PUT"])
@jwt_required()
def update_driver(driver_id):
    """更新驾驶员"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "无效的请求数据"}), 400
        
        # 获取当前用户ID
        user_id = get_jwt_identity()
        
        # 获取驾驶员
        driver = driver_dao.get_by_driver_id(driver_id)
        if not driver:
            return jsonify({"error": "驾驶员不存在"}), 404
        
        # 检查权限
        if driver.owner_id != user_id:
            return jsonify({"error": "无权修改该驾驶员"}), 403
        
        # 更新驾驶员
        name = data.get("name")
        is_active = data.get("is_active")
        
        update_data = {}
        if name is not None:
            update_data["name"] = name
        if is_active is not None:
            update_data["is_active"] = is_active
        
        if update_data:
            driver = driver_dao.update(driver.id, **update_data)
        
        return jsonify({"driver": driver.to_dict()})
    
    except Exception as e:
        logger.error(f"更新驾驶员错误: {e}")
        return jsonify({"error": "服务器内部错误"}), 500


@app.route(f"{API_PREFIX}/drivers/<string:driver_id>", methods=["DELETE"])
@jwt_required()
def delete_driver(driver_id):
    """删除驾驶员"""
    try:
        # 获取当前用户ID
        user_id = get_jwt_identity()
        
        # 获取驾驶员
        driver = driver_dao.get_by_driver_id(driver_id)
        if not driver:
            return jsonify({"error": "驾驶员不存在"}), 404
        
        # 检查权限
        if driver.owner_id != user_id:
            return jsonify({"error": "无权删除该驾驶员"}), 403
        
        # 删除驾驶员
        driver_dao.delete(driver.id)
        
        return jsonify({"message": "驾驶员已删除"})
    
    except Exception as e:
        logger.error(f"删除驾驶员错误: {e}")
        return jsonify({"error": "服务器内部错误"}), 500


# 事件相关API
@app.route(f"{API_PREFIX}/events", methods=["GET"])
@jwt_required()
def get_events():
    """获取事件列表"""
    try:
        # 获取当前用户ID
        user_id = get_jwt_identity()
        
        # 获取查询参数
        device_id = request.args.get("device_id")
        driver_id = request.args.get("driver_id")
        event_type = request.args.get("event_type")
        start_time_str = request.args.get("start_time")
        end_time_str = request.args.get("end_time")
        limit = request.args.get("limit", 100, type=int)
        
        # 构建过滤器
        filters = {}
        
        # 如果指定了设备ID
        if device_id:
            # 检查设备所有权
            device = device_dao.get_by_device_id(device_id)
            if not device:
                return jsonify({"error": "设备不存在"}), 404
            if device.owner_id != user_id:
                return jsonify({"error": "无权访问该设备的事件"}), 403
            
            filters["device_id"] = device_id
        
        # 如果指定了驾驶员ID
        if driver_id:
            # 检查驾驶员所有权
            driver = driver_dao.get_by_driver_id(driver_id)
            if not driver:
                return jsonify({"error": "驾驶员不存在"}), 404
            if driver.owner_id != user_id:
                return jsonify({"error": "无权访问该驾驶员的事件"}), 403
            
            filters["driver_id"] = driver_id
        
        # 如果指定了事件类型
        if event_type:
            filters["event_type"] = event_type
        
        # 处理时间范围
        start_time = None
        end_time = None
        
        if start_time_str:
            try:
                start_time = datetime.datetime.fromisoformat(start_time_str)
                filters["start_time"] = start_time
            except ValueError:
                return jsonify({"error": "开始时间格式无效"}), 400
        
        if end_time_str:
            try:
                end_time = datetime.datetime.fromisoformat(end_time_str)
                filters["end_time"] = end_time
            except ValueError:
                return jsonify({"error": "结束时间格式无效"}), 400
        
        # 搜索事件
        events = event_dao.search(filters, limit)
        
        # 转换为字典列表
        result = [event.to_dict() for event in events]
        
        return jsonify({"events": result})
    
    except Exception as e:
        logger.error(f"获取事件列表错误: {e}")
        return jsonify({"error": "服务器内部错误"}), 500


@app.route(f"{API_PREFIX}/events/<string:event_id>", methods=["GET"])
@jwt_required()
def get_event(event_id):
    """获取事件详情"""
    try:
        # 获取当前用户ID
        user_id = get_jwt_identity()
        
        # 获取事件
        event = event_dao.get_by_event_id(event_id)
        if not event:
            return jsonify({"error": "事件不存在"}), 404
        
        # 检查权限
        device = device_dao.get_by_device_id(event.device_id)
        if not device or device.owner_id != user_id:
            return jsonify({"error": "无权访问该事件"}), 403
        
        return jsonify({"event": event.to_dict()})
    
    except Exception as e:
        logger.error(f"获取事件详情错误: {e}")
        return jsonify({"error": "服务器内部错误"}), 500


@app.route(f"{API_PREFIX}/events", methods=["POST"])
def create_event():
    """创建事件 (客户端上报)"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "无效的请求数据"}), 400
        
        # 获取事件数据
        device_id = data.get("device_id")
        events_data = data.get("events")
        
        if not device_id or not events_data:
            return jsonify({"error": "设备ID和事件数据不能为空"}), 400
        
        # 检查设备是否存在
        device = device_dao.get_by_device_id(device_id)
        if not device:
            # 注：这里我们只记录错误，但仍接受来自未知设备的事件
            logger.warning(f"未知设备上报事件: {device_id}")
        else:
            # 更新设备最后在线时间
            device_dao.update_last_seen(device_id)
        
        # 处理事件
        created_events = []
        
        for event_data in events_data:
            driver_id = event_data.get("driver_id")
            event_type = event_data.get("event_type")
            confidence = event_data.get("confidence")
            timestamp_str = event_data.get("timestamp")
            details = event_data.get("details", {})
            
            if not driver_id or not event_type or confidence is None or not timestamp_str:
                logger.warning(f"跳过无效的事件数据: {event_data}")
                continue
            
            # 解析时间戳
            try:
                timestamp = datetime.datetime.fromisoformat(timestamp_str)
            except ValueError:
                logger.warning(f"无效的时间戳格式: {timestamp_str}")
                continue
            
            # 检查驾驶员是否存在
            driver = driver_dao.get_by_driver_id(driver_id)
            if not driver:
                logger.warning(f"未知驾驶员: {driver_id}")
            
            # 将详情转换为JSON字符串
            details_json = json.dumps(details)
            
            # 创建事件
            event = event_dao.create(
                device_id=device_id,
                driver_id=driver_id,
                event_type=event_type,
                confidence=confidence,
                timestamp=timestamp,
                details=details_json
            )
            
            created_events.append(event.to_dict())
        
        return jsonify({
            "message": f"成功接收{len(created_events)}个事件",
            "events": created_events
        })
    
    except Exception as e:
        logger.error(f"创建事件错误: {e}")
        return jsonify({"error": "服务器内部错误"}), 500


# 统计相关API
@app.route(f"{API_PREFIX}/stats/device/<string:device_id>", methods=["GET"])
@jwt_required()
def get_device_stats(device_id):
    """获取设备统计信息"""
    try:
        # 获取当前用户ID
        user_id = get_jwt_identity()
        
        # 检查设备所有权
        device = device_dao.get_by_device_id(device_id)
        if not device:
            return jsonify({"error": "设备不存在"}), 404
        if device.owner_id != user_id:
            return jsonify({"error": "无权访问该设备的统计信息"}), 403
        
        # 获取事件
        events = event_dao.get_by_device_id(device_id, 1000)  # 最多1000条
        
        # 分类统计
        event_types = {}
        events_by_day = {}
        total_events = len(events)
        latest_event = None
        
        for event in events:
            # 按类型统计
            event_type = event.event_type
            if event_type not in event_types:
                event_types[event_type] = 0
            event_types[event_type] += 1
            
            # 按日期统计
            day = event.timestamp.date().isoformat()
            if day not in events_by_day:
                events_by_day[day] = 0
            events_by_day[day] += 1
            
            # 最新事件
            if latest_event is None or event.timestamp > latest_event.timestamp:
                latest_event = event
        
        # 按日期排序
        sorted_days = sorted(events_by_day.keys())
        events_trend = [{"date": day, "count": events_by_day[day]} for day in sorted_days]
        
        # 结果
        stats = {
            "total_events": total_events,
            "event_types": [{"type": k, "count": v} for k, v in event_types.items()],
            "events_trend": events_trend,
            "latest_event": latest_event.to_dict() if latest_event else None
        }
        
        return jsonify({"stats": stats})
    
    except Exception as e:
        logger.error(f"获取设备统计信息错误: {e}")
        return jsonify({"error": "服务器内部错误"}), 500


@app.route(f"{API_PREFIX}/stats/driver/<string:driver_id>", methods=["GET"])
@jwt_required()
def get_driver_stats(driver_id):
    """获取驾驶员统计信息"""
    try:
        # 获取当前用户ID
        user_id = get_jwt_identity()
        
        # 检查驾驶员所有权
        driver = driver_dao.get_by_driver_id(driver_id)
        if not driver:
            return jsonify({"error": "驾驶员不存在"}), 404
        if driver.owner_id != user_id:
            return jsonify({"error": "无权访问该驾驶员的统计信息"}), 403
        
        # 获取事件
        events = event_dao.get_by_driver_id(driver_id, 1000)  # 最多1000条
        
        # 分类统计
        event_types = {}
        events_by_day = {}
        total_events = len(events)
        latest_event = None
        
        for event in events:
            # 按类型统计
            event_type = event.event_type
            if event_type not in event_types:
                event_types[event_type] = 0
            event_types[event_type] += 1
            
            # 按日期统计
            day = event.timestamp.date().isoformat()
            if day not in events_by_day:
                events_by_day[day] = 0
            events_by_day[day] += 1
            
            # 最新事件
            if latest_event is None or event.timestamp > latest_event.timestamp:
                latest_event = event
        
        # 按日期排序
        sorted_days = sorted(events_by_day.keys())
        events_trend = [{"date": day, "count": events_by_day[day]} for day in sorted_days]
        
        # 结果
        stats = {
            "total_events": total_events,
            "event_types": [{"type": k, "count": v} for k, v in event_types.items()],
            "events_trend": events_trend,
            "latest_event": latest_event.to_dict() if latest_event else None
        }
        
        return jsonify({"stats": stats})
    
    except Exception as e:
        logger.error(f"获取驾驶员统计信息错误: {e}")
        return jsonify({"error": "服务器内部错误"}), 500


# 系统相关API
@app.route(f"{API_PREFIX}/system/health", methods=["GET"])
def health_check():
    """健康检查"""
    return jsonify({
        "status": "ok",
        "version": config.api_version,
        "timestamp": datetime.datetime.now().isoformat()
    })


# 错误处理
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not Found"}), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Method Not Allowed"}), 405


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal Server Error"}), 500


# 初始化数据库
@app.before_first_request
def before_first_request():
    """在第一次请求之前初始化数据库"""
    init_db()


# 创建测试用户
def create_test_user():
    """创建测试用户"""
    try:
        # 检查是否已存在
        if user_dao.get_by_username("admin"):
            return
        
        # 创建管理员用户
        password_hash = generate_password_hash("admin123")
        user = user_dao.create(
            username="admin",
            email="admin@example.com",
            password_hash=password_hash,
            first_name="Admin",
            last_name="User",
            is_admin=True
        )
        
        logger.info(f"创建测试用户: {user.username}")
    
    except Exception as e:
        logger.error(f"创建测试用户错误: {e}")


# 应用程序上下文
@app.before_request
def before_request():
    """在请求之前"""
    g.start_time = time.time()


@app.after_request
def after_request(response):
    """在请求之后"""
    # 添加响应头
    response.headers.add("X-API-Version", config.api_version)
    
    # 计算请求处理时间
    if hasattr(g, "start_time"):
        elapsed = time.time() - g.start_time
        logger.debug(f"请求处理时间: {elapsed:.3f}秒 - {request.path}")
    
    return response


if __name__ == "__main__":
    # 初始化数据库
    init_db()
    
    # 创建测试用户
    create_test_user()
    
    # 启动服务器
    app.run(host=config.host, port=config.port, debug=config.debug)
