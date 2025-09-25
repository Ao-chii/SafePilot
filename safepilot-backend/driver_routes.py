from flask import Blueprint, request, jsonify
from models import db, Driver
import uuid

driver_bp = Blueprint('driver', __name__, url_prefix='/api/v1/drivers')

# 获取驾驶员列表
@driver_bp.route('', methods=['GET'])
def get_drivers():
    drivers = Driver.query.all()
    return jsonify([{
        'driver_id': driver.id,
        'name': driver.name,
        'is_active': driver.is_active,
        'created_at': driver.created_at.isoformat() if driver.created_at else None,
        'updated_at': driver.updated_at.isoformat() if driver.updated_at else None
    } for driver in drivers])

# 获取驾驶员详情
@driver_bp.route('/<driver_id>', methods=['GET'])
def get_driver(driver_id):
    driver = Driver.query.get(driver_id)
    if not driver:
        return jsonify({'error': 'Driver not found'}), 404
    
    return jsonify({
        'driver_id': driver.id,
        'name': driver.name,
        'is_active': driver.is_active,
        'created_at': driver.created_at.isoformat() if driver.created_at else None,
        'updated_at': driver.updated_at.isoformat() if driver.updated_at else None
    })

# 创建驾驶员
@driver_bp.route('', methods=['POST'])
def create_driver():
    data = request.get_json()
    
    # 验证必填字段
    if not data.get('driver_id') or not data.get('name'):
        return jsonify({'error': 'driver_id and name are required'}), 400
    
    # 检查驾驶员是否已存在
    existing_driver = Driver.query.get(data['driver_id'])
    if existing_driver:
        return jsonify({'error': 'Driver already exists'}), 400
    
    # 创建新驾驶员
    driver = Driver(
        id=data['driver_id'],
        name=data['name'],
        is_active=data.get('is_active', True)
    )
    
    db.session.add(driver)
    db.session.commit()
    
    return jsonify({
        'driver_id': driver.id,
        'name': driver.name,
        'is_active': driver.is_active,
        'created_at': driver.created_at.isoformat() if driver.created_at else None,
        'updated_at': driver.updated_at.isoformat() if driver.updated_at else None
    }), 201

# 更新驾驶员
@driver_bp.route('/<driver_id>', methods=['PUT'])
def update_driver(driver_id):
    driver = Driver.query.get(driver_id)
    if not driver:
        return jsonify({'error': 'Driver not found'}), 404
    
    data = request.get_json()
    
    # 更新驾驶员信息
    if 'name' in data:
        driver.name = data['name']
    if 'is_active' in data:
        driver.is_active = data['is_active']
    
    db.session.commit()
    
    return jsonify({
        'driver_id': driver.id,
        'name': driver.name,
        'is_active': driver.is_active,
        'created_at': driver.created_at.isoformat() if driver.created_at else None,
        'updated_at': driver.updated_at.isoformat() if driver.updated_at else None
    })

# 删除驾驶员
@driver_bp.route('/<driver_id>', methods=['DELETE'])
def delete_driver(driver_id):
    driver = Driver.query.get(driver_id)
    if not driver:
        return jsonify({'error': 'Driver not found'}), 404
    
    db.session.delete(driver)
    db.session.commit()
    
    return '', 204