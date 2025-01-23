import os
from datetime import timedelta
import urllib.parse

class Config:
    # 基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev'
    DEBUG = False if os.environ.get('FLASK_ENV') == 'production' else True
    
    # 数据库配置
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # 处理Render的postgres://格式
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        # 确保URL是正确的格式
        try:
            parsed = urllib.parse.urlparse(database_url)
            if parsed.scheme and parsed.netloc:
                SQLALCHEMY_DATABASE_URI = database_url
            else:
                SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
        except Exception as e:
            print(f"数据库URL解析错误: {e}")
            SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,  # 自动检测断开的连接
        'pool_recycle': 300,    # 5分钟回收连接
    }
    
    # 会话配置
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # 文件上传配置
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    
    # CORS配置
    CORS_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000']
    
    # JWT配置
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    @staticmethod
    def init_app(app):
        """初始化应用配置"""
        # 确保上传目录存在
        if not os.path.exists(Config.UPLOAD_FOLDER):
            os.makedirs(Config.UPLOAD_FOLDER)
        
        # 配置日志
        import logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[logging.StreamHandler()]
        )
        
        # 打印配置信息
        app.logger.info("=== 应用配置 ===")
        app.logger.info(f"环境: {'Production' if os.environ.get('FLASK_ENV') == 'production' else 'Development'}")
        app.logger.info(f"调试模式: {'开启' if app.debug else '关闭'}")
        # 打印数据库URL时隐藏敏感信息
        db_url = Config.SQLALCHEMY_DATABASE_URI
        if db_url.startswith('postgresql://'):
            parsed = urllib.parse.urlparse(db_url)
            safe_url = f"{parsed.scheme}://{parsed.username}:****@{parsed.hostname}:{parsed.port}/{parsed.path.lstrip('/')}"
            app.logger.info(f"数据库URL: {safe_url}")
        else:
            app.logger.info(f"数据库URL: {db_url}")
        app.logger.info(f"上传文件夹: {Config.UPLOAD_FOLDER}")
        app.logger.info(f"CORS配置: {Config.CORS_ORIGINS}") 