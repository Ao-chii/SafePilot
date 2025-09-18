# 服务器配置模块

import os
import json
import logging
from pathlib import Path

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("SafePilotServer")

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent.absolute()
DATA_DIR = ROOT_DIR / "data"
LOG_DIR = ROOT_DIR / "logs"

# 确保目录存在
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)


class ServerConfig:
    """服务器配置类 - 单例模式"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ServerConfig, cls).__new__(cls)
            cls._instance._load_default_config()
        return cls._instance
    
    def _load_default_config(self):
        """加载默认配置"""
        # 基础配置
        self.debug = False
        self.testing = False
        self.secret_key = os.environ.get("SECRET_KEY", "dev-key-change-in-production")
        
        # 服务器配置
        self.host = os.environ.get("HOST", "0.0.0.0")
        self.port = int(os.environ.get("PORT", 5000))
        
        # 数据库配置
        self.db_type = os.environ.get("DB_TYPE", "sqlite")  # sqlite, postgresql
        self.db_name = os.environ.get("DB_NAME", "safepilot")
        self.db_user = os.environ.get("DB_USER", "")
        self.db_password = os.environ.get("DB_PASSWORD", "")
        self.db_host = os.environ.get("DB_HOST", "")
        self.db_port = os.environ.get("DB_PORT", "")
        
        # SQLite 特定配置
        self.sqlite_path = os.environ.get("SQLITE_PATH", str(DATA_DIR / "safepilot.db"))
        
        # 安全配置
        self.jwt_secret_key = os.environ.get("JWT_SECRET_KEY", "jwt-dev-key-change-in-production")
        self.jwt_access_token_expires = int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRES", 3600))  # 1小时
        self.cors_origins = os.environ.get("CORS_ORIGINS", "*")
        
        # API配置
        self.api_prefix = "/api"
        self.api_version = "v1"
        
        # 尝试从配置文件加载
        self._load_from_file()
    
    def _load_from_file(self, config_file="server_config.json"):
        """从文件加载配置"""
        try:
            config_path = Path(config_file)
            if config_path.exists():
                with open(config_path, "r", encoding="utf-8") as f:
                    custom_config = json.load(f)
                    
                    # 更新配置
                    for key, value in custom_config.items():
                        setattr(self, key, value)
                
                logger.info(f"已从 {config_file} 加载配置")
        
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
    
    @property
    def database_uri(self):
        """获取数据库URI"""
        if self.db_type == "sqlite":
            return f"sqlite:///{self.sqlite_path}"
        
        elif self.db_type == "postgresql":
            return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        
        else:
            raise ValueError(f"不支持的数据库类型: {self.db_type}")


# 创建全局配置实例
config = ServerConfig()

if __name__ == "__main__":
    # 测试
    print(f"数据库URI: {config.database_uri}")
    print(f"API前缀: {config.api_prefix}")
    print(f"JWT过期时间: {config.jwt_access_token_expires}秒")
