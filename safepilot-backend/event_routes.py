from flask import Blueprint, request, jsonify
from models import db, Event
from datetime import datetime
import json

event_bp = Blueprint('event', __name__, url_prefix='/api/v1/events')

# 获取事件列表
@event_bp.route('', methods=['GET'])
def get_events():
    # 获取查询参数
    device_id = request.args.get('device_id')
    driver_id = request.args.get('driver_id')
    event_type = request.args.get('event_type')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    limit = request.args.get('limit', type=int)
    offset = request.args.get('offset', type=int, default=0)
    
    # 构建查询
    query = Event.query
    
    if device_id:
        query = query.filter(Event.device_id == device_id)
    
    if driver_id:
        query = query.filter(Event.driver_id == driver_id)
    
    if event_type:
        query = query.filter(Event.event_type == event_type)
    
    if start_time:
        try:
            start_dt = datetime.fromisoformat(start_time)
            query = query.filter(Event.timestamp >= start_dt)
        except ValueError:
            return jsonify({'error': 'Invalid start_time format'}), 400
    
    if end_time:
        try:
            end_dt = datetime.fromisoformat(end_time)
            query = query.filter(Event.timestamp <= end_dt)
        except ValueError:
            return jsonify({'error': 'Invalid end_time format'}), 400
    
    # 获取总记录数
    total = query.count()
    
    # 应用分页
    if offset:
        query = query.offset(offset)
    
    if limit:
        query = query.limit(limit)
    
    # 执行查询
    events = query.all()
    
    # 格式化结果
    result = []
    for event in events:
        event_data = {
            'id': event.id,
            'device_id': event.device_id,
            'driver_id': event.driver_id,
            'event_type': event.event_type,
            'confidence': float(event.confidence) if event.confidence else None,
            'timestamp': event.timestamp.isoformat() if event.timestamp else None,
            'details': event.details,
            'created_at': event.created_at.isoformat() if event.created_at else None
        }
        result.append(event_data)
    
    # 返回格式化响应
    return jsonify({
        'events': result,
        'total': total
    })

# 获取事件详情
@event_bp.route('/<int:event_id>', methods=['GET'])
def get_event(event_id):
    event = Event.query.get(event_id)
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    event_data = {
        'id': event.id,
        'device_id': event.device_id,
        'driver_id': event.driver_id,
        'event_type': event.event_type,
        'confidence': float(event.confidence) if event.confidence else None,
        'timestamp': event.timestamp.isoformat() if event.timestamp else None,
        'details': event.details,
        'created_at': event.created_at.isoformat() if event.created_at else None
    }
    
    return jsonify(event_data)

# 创建事件（客户端上报）
@event_bp.route('', methods=['POST'])
def create_events():
    data = request.get_json()
    
    # 验证必填字段
    if not data.get('device_id') or not data.get('events'):
        return jsonify({'error': 'device_id and events are required'}), 400
    
    device_id = data['device_id']
    events_data = data['events']
    
    # 验证事件数组
    if not isinstance(events_data, list):
        return jsonify({'error': 'events must be an array'}), 400
    
    created_events = []
    
    # 处理每个事件
    for event_data in events_data:
        # 验证事件必填字段
        required_fields = ['driver_id', 'event_type', 'confidence', 'timestamp']
        for field in required_fields:
            if field not in event_data:
                return jsonify({'error': f'Missing required field: {field} in event data'}), 400
        
        # 解析时间戳
        try:
            timestamp = datetime.fromisoformat(event_data['timestamp'])
        except ValueError:
            return jsonify({'error': f'Invalid timestamp format: {event_data["timestamp"]}'}), 400
        
        # 验证数值字段
        try:
            confidence = float(event_data['confidence'])
            # 检查confidence是否在有效范围内 (0.00-1.00)
            if confidence < 0 or confidence > 1:
                return jsonify({'error': 'Confidence must be between 0 and 1'}), 400
        except (ValueError, TypeError):
            return jsonify({'error': 'Confidence must be a valid number'}), 400
        
        # 创建事件
        event = Event(
            device_id=device_id,
            driver_id=event_data['driver_id'],
            event_type=event_data['event_type'],
            confidence=confidence,
            timestamp=timestamp,
            details=event_data.get('details')
        )
        
        db.session.add(event)
        created_events.append(event)
    
    # 提交到数据库
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create events'}), 500
    
    # 返回创建的事件信息
    result = []
    for event in created_events:
        event_data = {
            'id': event.id,
            'device_id': event.device_id,
            'driver_id': event.driver_id,
            'event_type': event.event_type,
            'confidence': float(event.confidence) if event.confidence else None,
            'timestamp': event.timestamp.isoformat() if event.timestamp else None,
            'details': event.details,
            'created_at': event.created_at.isoformat() if event.created_at else None
        }
        result.append(event_data)
    
    return jsonify(result), 201