from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

# 用户表
class User(db.Model):
    __tablename__ = 'users'
    __table_args__ = {'sqlite_autoincrement': True}
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50))
    phone = db.Column(db.String(20), nullable=False)
    role = db.Column(db.Enum('driver', 'admin', 'supervisor'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    alerts = db.relationship('Alert', back_populates='handler')
    password_reset_codes = db.relationship('PasswordResetCode', back_populates='user')

# 密码重置验证码表
class PasswordResetCode(db.Model):
    __tablename__ = 'password_reset_codes'
    __table_args__ = {'sqlite_autoincrement': True}
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    contact = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(10), nullable=False)
    type = db.Column(db.Enum('email', 'phone'), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', back_populates='password_reset_codes')

# 设备表
class Device(db.Model):
    __tablename__ = 'devices'
    
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    events = db.relationship('Event', back_populates='device')
    video_streams = db.relationship('VideoStream', back_populates='device')
    alerts = db.relationship('Alert', back_populates='device')
    device_stats = db.relationship('DeviceStat', back_populates='device')

# 驾驶员表
class Driver(db.Model):
    __tablename__ = 'drivers'
    
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    events = db.relationship('Event', back_populates='driver')
    driver_stats = db.relationship('DriverStat', back_populates='driver')

# 事件表
class Event(db.Model):
    __tablename__ = 'events'
    __table_args__ = {'sqlite_autoincrement': True}
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    device_id = db.Column(db.String(50), db.ForeignKey('devices.id'))
    driver_id = db.Column(db.String(50), db.ForeignKey('drivers.id'))
    event_type = db.Column(db.String(50), nullable=False)
    confidence = db.Column(db.Numeric(3, 2), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    details = db.Column(db.JSON)
    image = db.Column(db.Text, nullable=True)  # 新增图片字段
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    device = db.relationship('Device', back_populates='events')
    driver = db.relationship('Driver', back_populates='events')

# 设备统计数据表
class DeviceStat(db.Model):
    __tablename__ = 'device_stats'
    __table_args__ = {'sqlite_autoincrement': True}
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    device_id = db.Column(db.String(50), db.ForeignKey('devices.id'))
    stat_type = db.Column(db.String(50), nullable=False)
    stat_value = db.Column(db.JSON, nullable=False)
    recorded_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    device = db.relationship('Device', back_populates='device_stats')

# 驾驶员统计数据表
class DriverStat(db.Model):
    __tablename__ = 'driver_stats'
    __table_args__ = {'sqlite_autoincrement': True}
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    driver_id = db.Column(db.String(50), db.ForeignKey('drivers.id'))
    stat_type = db.Column(db.String(50), nullable=False)
    stat_value = db.Column(db.JSON, nullable=False)
    recorded_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    driver = db.relationship('Driver', back_populates='driver_stats')

# 视频流表
class VideoStream(db.Model):
    __tablename__ = 'video_streams'
    
    id = db.Column(db.String(50), primary_key=True)
    device_id = db.Column(db.String(50), db.ForeignKey('devices.id'))
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    device = db.relationship('Device', back_populates='video_streams')

# 告警表
class Alert(db.Model):
    __tablename__ = 'alerts'
    
    id = db.Column(db.String(50), primary_key=True)
    device_id = db.Column(db.String(50), db.ForeignKey('devices.id'))
    alert_level = db.Column(db.Enum('low', 'medium', 'high', 'critical'), nullable=False)
    alert_type = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=False)
    details = db.Column(db.JSON)
    handled = db.Column(db.Boolean, default=False)
    handled_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    handled_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    device = db.relationship('Device', back_populates='alerts')
    handler = db.relationship('User', back_populates='alerts')