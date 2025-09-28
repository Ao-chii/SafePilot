from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from models import db
import os

# 导入路由蓝图
from device_routes import device_bp
from driver_routes import driver_bp
from event_routes import event_bp

# 确保实例文件夹存在
instance_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance')
if not os.path.exists(instance_path):
    os.makedirs(instance_path)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(instance_path, 'safepilot.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 初始化数据库
db.init_app(app)

# 允许所有跨域请求（仅开发环境）
CORS(app)

# 注册路由蓝图
app.register_blueprint(device_bp)
app.register_blueprint(driver_bp)
app.register_blueprint(event_bp)

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'

def init_db():
    """初始化数据库"""
    with app.app_context():
        # 创建所有表
        db.create_all()

if __name__ == '__main__':
    # 初始化数据库
    with app.app_context():
        db.create_all()
    app.run()