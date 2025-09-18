# 数据模型模块

import datetime
import uuid
from typing import Dict, Any, List, Optional

from sqlalchemy import (
    Column, Integer, String, Float, DateTime,
    Boolean, ForeignKey, Text, create_engine
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, scoped_session
from sqlalchemy.sql import func

from server.config import config

# 创建数据库引擎
engine = create_engine(config.database_uri, echo=config.debug)

# 创建会话工厂
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

# 创建基类
Base = declarative_base()


class User(Base):
    """用户模型"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # 关系
    devices = relationship("Device", back_populates="owner")
    drivers = relationship("Driver", back_populates="owner")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "is_admin": self.is_admin,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class Device(Base):
    """设备模型"""
    __tablename__ = 'devices'
    
    id = Column(Integer, primary_key=True)
    device_id = Column(String(100), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(200), nullable=True)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    is_active = Column(Boolean, default=True)
    last_seen = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # 关系
    owner = relationship("User", back_populates="devices")
    events = relationship("Event", back_populates="device")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "device_id": self.device_id,
            "name": self.name,
            "description": self.description,
            "owner_id": self.owner_id,
            "is_active": self.is_active,
            "last_seen": self.last_seen.isoformat() if self.last_seen else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class Driver(Base):
    """驾驶员模型"""
    __tablename__ = 'drivers'
    
    id = Column(Integer, primary_key=True)
    driver_id = Column(String(100), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # 关系
    owner = relationship("User", back_populates="drivers")
    events = relationship("Event", back_populates="driver")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "driver_id": self.driver_id,
            "name": self.name,
            "owner_id": self.owner_id,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class Event(Base):
    """事件模型"""
    __tablename__ = 'events'
    
    id = Column(Integer, primary_key=True)
    event_id = Column(String(100), unique=True, default=lambda: str(uuid.uuid4()))
    device_id = Column(String(100), ForeignKey('devices.device_id'), nullable=False)
    driver_id = Column(String(100), ForeignKey('drivers.driver_id'), nullable=False)
    event_type = Column(String(50), nullable=False)
    confidence = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    details = Column(Text, nullable=True)  # JSON字符串
    image_path = Column(String(200), nullable=True)
    is_processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    
    # 关系
    device = relationship("Device", back_populates="events")
    driver = relationship("Driver", back_populates="events")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        import json
        
        details_dict = {}
        if self.details:
            try:
                details_dict = json.loads(self.details)
            except:
                details_dict = {"raw": self.details}
        
        return {
            "id": self.id,
            "event_id": self.event_id,
            "device_id": self.device_id,
            "driver_id": self.driver_id,
            "event_type": self.event_type,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "details": details_dict,
            "image_path": self.image_path,
            "is_processed": self.is_processed,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


# 创建表
def init_db():
    """初始化数据库"""
    Base.metadata.create_all(bind=engine)
    print("数据库表已创建")


# 数据访问对象基类
class BaseDAO:
    """数据访问对象基类"""
    
    def __init__(self, model_class):
        self.model_class = model_class
    
    def get_session(self):
        """获取会话"""
        return Session()
    
    def get_by_id(self, id: int) -> Optional[Any]:
        """通过ID获取"""
        session = self.get_session()
        try:
            return session.query(self.model_class).get(id)
        finally:
            session.close()
    
    def get_all(self) -> List[Any]:
        """获取所有"""
        session = self.get_session()
        try:
            return session.query(self.model_class).all()
        finally:
            session.close()
    
    def create(self, **kwargs) -> Any:
        """创建"""
        session = self.get_session()
        try:
            obj = self.model_class(**kwargs)
            session.add(obj)
            session.commit()
            return obj
        finally:
            session.close()
    
    def update(self, id: int, **kwargs) -> Optional[Any]:
        """更新"""
        session = self.get_session()
        try:
            obj = session.query(self.model_class).get(id)
            if obj:
                for key, value in kwargs.items():
                    setattr(obj, key, value)
                session.commit()
            return obj
        finally:
            session.close()
    
    def delete(self, id: int) -> bool:
        """删除"""
        session = self.get_session()
        try:
            obj = session.query(self.model_class).get(id)
            if obj:
                session.delete(obj)
                session.commit()
                return True
            return False
        finally:
            session.close()


# 用户数据访问对象
class UserDAO(BaseDAO):
    """用户数据访问对象"""
    
    def __init__(self):
        super().__init__(User)
    
    def get_by_username(self, username: str) -> Optional[User]:
        """通过用户名获取"""
        session = self.get_session()
        try:
            return session.query(User).filter_by(username=username).first()
        finally:
            session.close()
    
    def get_by_email(self, email: str) -> Optional[User]:
        """通过邮箱获取"""
        session = self.get_session()
        try:
            return session.query(User).filter_by(email=email).first()
        finally:
            session.close()


# 设备数据访问对象
class DeviceDAO(BaseDAO):
    """设备数据访问对象"""
    
    def __init__(self):
        super().__init__(Device)
    
    def get_by_device_id(self, device_id: str) -> Optional[Device]:
        """通过设备ID获取"""
        session = self.get_session()
        try:
            return session.query(Device).filter_by(device_id=device_id).first()
        finally:
            session.close()
    
    def get_by_owner_id(self, owner_id: int) -> List[Device]:
        """通过所有者ID获取"""
        session = self.get_session()
        try:
            return session.query(Device).filter_by(owner_id=owner_id).all()
        finally:
            session.close()
    
    def update_last_seen(self, device_id: str) -> Optional[Device]:
        """更新最后在线时间"""
        session = self.get_session()
        try:
            device = session.query(Device).filter_by(device_id=device_id).first()
            if device:
                device.last_seen = datetime.datetime.now()
                session.commit()
            return device
        finally:
            session.close()


# 驾驶员数据访问对象
class DriverDAO(BaseDAO):
    """驾驶员数据访问对象"""
    
    def __init__(self):
        super().__init__(Driver)
    
    def get_by_driver_id(self, driver_id: str) -> Optional[Driver]:
        """通过驾驶员ID获取"""
        session = self.get_session()
        try:
            return session.query(Driver).filter_by(driver_id=driver_id).first()
        finally:
            session.close()
    
    def get_by_owner_id(self, owner_id: int) -> List[Driver]:
        """通过所有者ID获取"""
        session = self.get_session()
        try:
            return session.query(Driver).filter_by(owner_id=owner_id).all()
        finally:
            session.close()


# 事件数据访问对象
class EventDAO(BaseDAO):
    """事件数据访问对象"""
    
    def __init__(self):
        super().__init__(Event)
    
    def get_by_event_id(self, event_id: str) -> Optional[Event]:
        """通过事件ID获取"""
        session = self.get_session()
        try:
            return session.query(Event).filter_by(event_id=event_id).first()
        finally:
            session.close()
    
    def get_by_device_id(self, device_id: str, limit: int = 100) -> List[Event]:
        """通过设备ID获取"""
        session = self.get_session()
        try:
            return session.query(Event) \
                .filter_by(device_id=device_id) \
                .order_by(Event.timestamp.desc()) \
                .limit(limit) \
                .all()
        finally:
            session.close()
    
    def get_by_driver_id(self, driver_id: str, limit: int = 100) -> List[Event]:
        """通过驾驶员ID获取"""
        session = self.get_session()
        try:
            return session.query(Event) \
                .filter_by(driver_id=driver_id) \
                .order_by(Event.timestamp.desc()) \
                .limit(limit) \
                .all()
        finally:
            session.close()
    
    def get_by_type(self, event_type: str, limit: int = 100) -> List[Event]:
        """通过事件类型获取"""
        session = self.get_session()
        try:
            return session.query(Event) \
                .filter_by(event_type=event_type) \
                .order_by(Event.timestamp.desc()) \
                .limit(limit) \
                .all()
        finally:
            session.close()
    
    def get_by_time_range(self, start_time: datetime.datetime, 
                         end_time: datetime.datetime, limit: int = 100) -> List[Event]:
        """通过时间范围获取"""
        session = self.get_session()
        try:
            return session.query(Event) \
                .filter(Event.timestamp >= start_time) \
                .filter(Event.timestamp <= end_time) \
                .order_by(Event.timestamp.desc()) \
                .limit(limit) \
                .all()
        finally:
            session.close()
    
    def search(self, filters: Dict[str, Any], limit: int = 100) -> List[Event]:
        """高级搜索"""
        session = self.get_session()
        try:
            query = session.query(Event)
            
            # 应用过滤器
            for key, value in filters.items():
                if hasattr(Event, key):
                    query = query.filter(getattr(Event, key) == value)
            
            return query.order_by(Event.timestamp.desc()).limit(limit).all()
        finally:
            session.close()


# 创建DAO实例
user_dao = UserDAO()
device_dao = DeviceDAO()
driver_dao = DriverDAO()
event_dao = EventDAO()


if __name__ == "__main__":
    # 初始化数据库
    init_db()
    
    # 测试创建用户
    user = user_dao.create(
        username="admin",
        email="admin@example.com",
        password_hash="hashed_password",
        first_name="Admin",
        last_name="User",
        is_admin=True
    )
    
    print(f"创建用户: {user.to_dict()}")
    
    # 测试创建设备
    device = device_dao.create(
        device_id="test_device_1",
        name="测试设备1",
        description="这是一个测试设备",
        owner_id=user.id
    )
    
    print(f"创建设备: {device.to_dict()}")
    
    # 测试创建驾驶员
    driver = driver_dao.create(
        driver_id="test_driver_1",
        name="测试驾驶员1",
        owner_id=user.id
    )
    
    print(f"创建驾驶员: {driver.to_dict()}")
    
    # 测试创建事件
    import json
    
    event = event_dao.create(
        device_id=device.device_id,
        driver_id=driver.driver_id,
        event_type="eyes_closed",
        confidence=0.95,
        timestamp=datetime.datetime.now(),
        details=json.dumps({"duration": 2.5, "eye_ratio": 0.1})
    )
    
    print(f"创建事件: {event.to_dict()}")
    
    print("测试完成")
