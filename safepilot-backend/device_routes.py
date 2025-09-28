from flask import Blueprint, request, jsonify
from models import db, Device
import uuid

device_bp = Blueprint('device', __name__, url_prefix='/api/v1/devices')

# 获取设备列表
@device_bp.route('', methods=['GET'])
def get_devices():
    devices = Device.query.all()
    return jsonify([{
        'device_id': device.id,
        'name': device.name,
        'description': device.description,
        'is_active': device.is_active,
        'created_at': device.created_at.isoformat() if device.created_at else None,
        'updated_at': device.updated_at.isoformat() if device.updated_at else None
    } for device in devices])

# 获取设备详情
@device_bp.route('/<device_id>', methods=['GET'])
def get_device(device_id):
    device = Device.query.get(device_id)
    if not device:
        return jsonify({'error': 'Device not found'}), 404
    
    return jsonify({
        'device_id': device.id,
        'name': device.name,
        'description': device.description,
        'is_active': device.is_active,
        'created_at': device.created_at.isoformat() if device.created_at else None,
        'updated_at': device.updated_at.isoformat() if device.updated_at else None
    })

# 创建设备
@device_bp.route('', methods=['POST'])
def create_device():
    data = request.get_json()
    
    # 验证必填字段
    if not data.get('device_id') or not data.get('name'):
        return jsonify({'error': 'device_id and name are required'}), 400
    
    # 检查设备是否已存在
    existing_device = Device.query.get(data['device_id'])
    if existing_device:
        return jsonify({'error': 'Device already exists'}), 400
    
    # 创建新设备
    device = Device(
        id=data['device_id'],
        name=data['name'],
        description=data.get('description', ''),
        is_active=data.get('is_active', True)
    )
    
    db.session.add(device)
    db.session.commit()
    
    return jsonify({
        'device_id': device.id,
        'name': device.name,
        'description': device.description,
        'is_active': device.is_active,
        'created_at': device.created_at.isoformat() if device.created_at else None,
        'updated_at': device.updated_at.isoformat() if device.updated_at else None
    }), 201

# 更新设备
@device_bp.route('/<device_id>', methods=['PUT'])
def update_device(device_id):
    device = Device.query.get(device_id)
    if not device:
        return jsonify({'error': 'Device not found'}), 404
    
    data = request.get_json()
    
    # 更新设备信息
    if 'name' in data:
        device.name = data['name']
    if 'description' in data:
        device.description = data['description']
    if 'is_active' in data:
        device.is_active = data['is_active']
    
    db.session.commit()
    
    return jsonify({
        'device_id': device.id,
        'name': device.name,
        'description': device.description,
        'is_active': device.is_active,
        'created_at': device.created_at.isoformat() if device.created_at else None,
        'updated_at': device.updated_at.isoformat() if device.updated_at else None
    })

# 删除设备
@device_bp.route('/<device_id>', methods=['DELETE'])
def delete_device(device_id):
    device = Device.query.get(device_id)
    if not device:
        return jsonify({'error': 'Device not found'}), 404
    
    db.session.delete(device)
    db.session.commit()
    
    return '', 204