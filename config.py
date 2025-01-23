import os
import mimetypes
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # 基本配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev'
    DEBUG = True
    TESTING = False
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@localhost/billing?charset=utf8mb4'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True  # 启用 SQL 语句日志
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 60,  # 每60秒回收连接
        'pool_timeout': 10,  # 连接超时时间10秒
        'pool_size': 20,  # 连接池大小
        'max_overflow': 10,  # 最大溢出连接数
        'pool_pre_ping': True,  # 每次请求前ping一下数据库，确保连接有效
        'echo': True,
        'echo_pool': True,
        'connect_args': {
            'charset': 'utf8mb4',
            'connect_timeout': 5,  # 连接超时5秒
            'read_timeout': 10,  # 读取超时10秒
            'write_timeout': 10  # 写入超时10秒
        }
    }
    
    # 安全配置
    WTF_CSRF_ENABLED = True  # 启用 CSRF 保护
    SESSION_COOKIE_SECURE = False  # 开发环境不需要 HTTPS
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 3600  # 1小时
    
    # 静态文件配置
    STATIC_FOLDER = os.path.join(basedir, 'app', 'static')
    STATIC_URL_PATH = '/static'
    SEND_FILE_MAX_AGE_DEFAULT = 0  # 禁用静态文件缓存
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 限制上传文件大小为16MB
    
    # 模板配置
    TEMPLATES_AUTO_RELOAD = True
    TEMPLATE_FOLDER = os.path.join(basedir, 'app', 'templates')
    EXPLAIN_TEMPLATE_LOADING = True  # 启用模板加载调试
    
    # 日志配置
    LOG_LEVEL = 'DEBUG'
    LOG_FORMAT = '%(asctime)s [%(levelname)s] %(message)s'
    LOG_FILE = os.path.join(basedir, 'logs', 'app.log')
    
    @staticmethod
    def init_app(app):
        """初始化应用配置"""
        # 确保日志目录存在
        log_dir = os.path.dirname(Config.LOG_FILE)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # 确保静态文件目录存在
        if not os.path.exists(Config.STATIC_FOLDER):
            os.makedirs(Config.STATIC_FOLDER)
            # 创建子目录
            for subdir in ['js', 'css', 'img', 'fonts', 'assets']:
                subdir_path = os.path.join(Config.STATIC_FOLDER, subdir)
                if not os.path.exists(subdir_path):
                    os.makedirs(subdir_path)
        
        # 确保模板目录存在
        if not os.path.exists(Config.TEMPLATE_FOLDER):
            os.makedirs(Config.TEMPLATE_FOLDER)
        
        # 配置日志
        import logging
        logging.basicConfig(
            level=getattr(logging, Config.LOG_LEVEL),
            format=Config.LOG_FORMAT,
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(Config.LOG_FILE)
            ]
        )
        
        # 配置应用
        app.config['SEND_FILE_MAX_AGE_DEFAULT'] = Config.SEND_FILE_MAX_AGE_DEFAULT
        app.config['TEMPLATES_AUTO_RELOAD'] = Config.TEMPLATES_AUTO_RELOAD
        app.config['STATIC_FOLDER'] = Config.STATIC_FOLDER
        app.config['STATIC_URL_PATH'] = Config.STATIC_URL_PATH
        app.config['TEMPLATE_FOLDER'] = Config.TEMPLATE_FOLDER
        app.config['EXPLAIN_TEMPLATE_LOADING'] = Config.EXPLAIN_TEMPLATE_LOADING
        app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH
        
        # 配置Jinja2
        app.jinja_env.auto_reload = True
        app.jinja_env.cache = {}
        
        # 打印配置信息
        print("\n=== 应用配置 ===")
        print(f"[DEBUG] 静态文件夹: {app.config['STATIC_FOLDER']}")
        print(f"[DEBUG] 静态URL路径: {app.config['STATIC_URL_PATH']}")
        print(f"[DEBUG] 模板文件夹: {app.config['TEMPLATE_FOLDER']}")
        print(f"[DEBUG] 已注册的蓝图: {list(app.blueprints.keys())}")
        
        # 检查静态文件
        if os.path.exists(app.config['STATIC_FOLDER']):
            print("\n=== 静态文件检查 ===")
            for root, dirs, files in os.walk(app.config['STATIC_FOLDER']):
                rel_path = os.path.relpath(root, app.config['STATIC_FOLDER'])
                print(f"[DEBUG] 目录: {rel_path}")
                for f in files:
                    file_path = os.path.join(root, f)
                    size = os.path.getsize(file_path)
                    mode = oct(os.stat(file_path).st_mode)[-3:]
                    mime_type, _ = mimetypes.guess_type(file_path)
                    print(f"[DEBUG]   - {f} ({size} bytes, {mode}, {mime_type})")
        
        return app