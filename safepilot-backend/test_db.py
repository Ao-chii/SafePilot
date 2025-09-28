from app import app, db
from models import User, Device, Driver, Event
import os

def test_db_creation():
    """测试数据库表创建"""
    print("开始测试数据库表创建...")
    
    # 确保实例文件夹存在
    instance_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance')
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)
        print("创建instance目录")
    
    with app.app_context():
        # 创建所有表
        db.create_all()
        print("已创建所有表")
        
        # 检查表是否创建成功
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"数据库中的表: {tables}")
        
        # 检查特定表是否存在
        expected_tables = ['users', 'devices', 'drivers', 'events', 'device_stats', 'driver_stats', 
                          'video_streams', 'alerts', 'password_reset_codes']
        
        missing_tables = []
        for table in expected_tables:
            if table not in tables:
                missing_tables.append(table)
        
        if missing_tables:
            print(f"缺少的表: {missing_tables}")
        else:
            print("所有表都已成功创建!")
            
        # 测试插入数据
        try:
            # 检查是否已存在测试数据
            existing_device = Device.query.filter_by(id="device001").first()
            if not existing_device:
                # 创建测试设备
                device = Device(id="device001", name="测试设备")
                db.session.add(device)
                
                # 创建测试驾驶员
                driver = Driver(id="driver001", name="测试驾驶员")
                db.session.add(driver)
                
                # 创建测试事件
                from datetime import datetime
                event = Event(device_id="device001", driver_id="driver001", 
                             event_type="test_event", confidence=0.95, 
                             timestamp=datetime.utcnow())
                db.session.add(event)
                
                # 提交事务
                db.session.commit()
                print("测试数据插入成功!")
            else:
                print("测试数据已存在，跳过插入")
                
        except Exception as e:
            db.session.rollback()
            print(f"测试数据插入失败: {e}")
        
        print("数据库测试完成")

if __name__ == "__main__":
    test_db_creation()