#!/usr/bin/env python3
# SafePilot 服务器启动脚本

import os
import sys
import argparse
import logging
import json
from pathlib import Path

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('safepilot_server.log')
    ]
)
logger = logging.getLogger("SafePilotServer")

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='SafePilot 服务器')
    
    parser.add_argument('--host', type=str, default=None,
                       help='主机地址 (默认: 0.0.0.0)')
    
    parser.add_argument('--port', type=int, default=None,
                       help='端口 (默认: 5000)')
    
    parser.add_argument('--debug', action='store_true',
                       help='调试模式')
    
    parser.add_argument('--db', type=str, default=None,
                       help='数据库类型 (sqlite/postgresql)')
    
    parser.add_argument('--db-path', type=str, default=None,
                       help='SQLite数据库路径')
    
    parser.add_argument('--db-name', type=str, default=None,
                       help='PostgreSQL数据库名')
    
    parser.add_argument('--db-user', type=str, default=None,
                       help='PostgreSQL用户名')
    
    parser.add_argument('--db-password', type=str, default=None,
                       help='PostgreSQL密码')
    
    parser.add_argument('--db-host', type=str, default=None,
                       help='PostgreSQL主机地址')
    
    parser.add_argument('--db-port', type=str, default=None,
                       help='PostgreSQL端口')
    
    parser.add_argument('--config', type=str, default=None,
                       help='配置文件路径')
    
    parser.add_argument('--init-db', action='store_true',
                       help='初始化数据库并退出')
    
    return parser.parse_args()

def load_config_from_file(config_file):
    """从文件加载配置"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"加载配置文件失败: {e}")
        return None

def main():
    """主函数"""
    # 解析命令行参数
    args = parse_args()
    
    # 导入服务器配置
    try:
        from server.config import config
    except ImportError:
        logger.error("无法导入服务器配置，请确保安装了所有依赖")
        sys.exit(1)
    
    # 首先从配置文件加载
    if args.config:
        config_file = Path(args.config)
        if config_file.exists():
            logger.info(f"从文件加载配置: {config_file}")
            custom_config = load_config_from_file(config_file)
            if custom_config:
                for key, value in custom_config.items():
                    setattr(config, key, value)
    
    # 然后应用命令行参数（覆盖配置文件）
    if args.host:
        config.host = args.host
    
    if args.port:
        config.port = args.port
    
    if args.debug:
        config.debug = True
    
    if args.db:
        config.db_type = args.db
    
    if args.db_path:
        config.sqlite_path = args.db_path
    
    if args.db_name:
        config.db_name = args.db_name
    
    if args.db_user:
        config.db_user = args.db_user
    
    if args.db_password:
        config.db_password = args.db_password
    
    if args.db_host:
        config.db_host = args.db_host
    
    if args.db_port:
        config.db_port = args.db_port
    
    # 显示配置信息
    logger.info("=== SafePilot 服务器配置 ===")
    logger.info(f"主机: {config.host}")
    logger.info(f"端口: {config.port}")
    logger.info(f"调试模式: {config.debug}")
    logger.info(f"数据库类型: {config.db_type}")
    
    if config.db_type == 'sqlite':
        logger.info(f"SQLite数据库路径: {config.sqlite_path}")
    elif config.db_type == 'postgresql':
        logger.info(f"PostgreSQL数据库: {config.db_name}")
        logger.info(f"PostgreSQL主机: {config.db_host}")
        logger.info(f"PostgreSQL端口: {config.db_port}")
    
    # 如果只是初始化数据库
    if args.init_db:
        from server.models import init_db
        logger.info("初始化数据库...")
        init_db()
        logger.info("数据库初始化完成")
        return 0
    
    # 导入API模块
    try:
        from server.api import app
    except ImportError:
        logger.error("无法导入API模块，请确保安装了所有依赖")
        sys.exit(1)
    
    # 启动服务器
    logger.info("启动SafePilot服务器...")
    app.run(host=config.host, port=config.port, debug=config.debug)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
