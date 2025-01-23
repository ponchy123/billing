import os
import logging
from logging.handlers import RotatingFileHandler
from flask import request, current_app
from flask_login import current_user
from functools import wraps
from datetime import datetime
from app import db
from app.models import Log

class Logger:
    """统一的日志工具类"""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
            
    def init_app(self, app):
        """初始化日志系统"""
        # 创建日志目录
        log_dir = os.path.join(app.root_path, 'logs')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        # 设置日志文件路径
        log_file = os.path.join(log_dir, 'app.log')
        
        # 创建文件处理器
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=10
        )
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        
        # 设置日志格式
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 设置日志级别
        file_handler.setLevel(logging.INFO)
        console_handler.setLevel(logging.DEBUG)
        
        # 创建日志记录器
        self.logger = logging.getLogger('app')
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # 添加处理器到应用日志记录器
        app.logger.addHandler(file_handler)
        app.logger.addHandler(console_handler)
        
        # 注册请求处理函数
        app.before_request(self.log_request)
        app.after_request(self.log_response)
    
    def log_info(self, message):
        """记录信息日志"""
        self.logger.info(message)
        
    def log_error(self, message):
        """记录错误日志"""
        self.logger.error(message)
        
    def log_warning(self, message):
        """记录警告日志"""
        self.logger.warning(message)
        
    def log_debug(self, message):
        """记录调试日志"""
        self.logger.debug(message)
    
    def log_request(self):
        """记录请求信息"""
        if current_app:
            user_id = current_user.id if current_user.is_authenticated else None
            self.logger.info(
                'Request: %s %s [User: %s] [IP: %s]',
                request.method,
                request.url,
                user_id,
                request.remote_addr
            )
            
    def log_response(self, response):
        """记录响应信息"""
        if current_app:
            self.logger.info(
                'Response: [Status: %s] [Size: %s]',
                response.status,
                len(response.get_data())
            )
        return response
        
    def log_error_response(self, error):
        """记录错误响应日志"""
        if current_app:
            user_id = current_user.id if current_user.is_authenticated else None
            self.logger.error(
                'Error: %s [User: %s] [URL: %s] [IP: %s]',
                str(error),
                user_id,
                request.url if request else None,
                request.remote_addr if request else None
            )
            
    def log_auth(self, event, user_id, success, message=None):
        """记录认证事件"""
        if current_app:
            self.logger.info(
                'Auth: %s [User: %s] [Success: %s] [Message: %s] [IP: %s]',
                event,
                user_id,
                success,
                message,
                request.remote_addr if request else None
            )
            
    def log_operation(self, operation, user_id, target_type, target_id, success, message=None):
        """记录操作事件"""
        if current_app:
            self.logger.info(
                'Operation: %s [User: %s] [Target: %s:%s] [Success: %s] [Message: %s]',
                operation,
                user_id,
                target_type,
                target_id,
                success,
                message
            )
            
    def log_calculation(self, user_id, input_data, result, success, message=None):
        """记录计算事件"""
        if current_app:
            self.logger.info(
                'Calculation: [User: %s] [Input: %s] [Result: %s] [Success: %s] [Message: %s]',
                user_id,
                input_data,
                result,
                success,
                message
            )
            
    def log_import_export(self, operation, user_id, file_type, file_name, success, message=None):
        """记录导入导出事件"""
        if current_app:
            self.logger.info(
                'ImportExport: %s [User: %s] [Type: %s] [File: %s] [Success: %s] [Message: %s]',
                operation,
                user_id,
                file_type,
                file_name,
                success,
                message
            )
    
    @staticmethod
    def operation_logger(operation_type):
        """操作日志装饰器"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                # 记录操作开始
                start_time = datetime.now()
                user_id = current_user.id if current_user.is_authenticated else None
                current_app.logger.info(f'Operation [{operation_type}] started - User: {user_id}')
                
                try:
                    # 执行操作
                    result = f(*args, **kwargs)
                    
                    # 记录操作成功
                    end_time = datetime.now()
                    duration = (end_time - start_time).total_seconds()
                    current_app.logger.info(
                        f'Operation [{operation_type}] completed - '
                        f'User: {user_id}, Duration: {duration}s'
                    )
                    
                    return result
                    
                except Exception as e:
                    # 记录操作失败
                    end_time = datetime.now()
                    duration = (end_time - start_time).total_seconds()
                    current_app.logger.error(
                        f'Operation [{operation_type}] failed - '
                        f'User: {user_id}, Duration: {duration}s, Error: {str(e)}'
                    )
                    raise
                    
            return decorated_function
        return decorator

def log_operation(operation_type, target_type, target_id=None, description=None):
    """记录操作日志
    
    Args:
        operation_type: 操作类型（login, logout, create, update, delete, import, export）
        target_type: 操作对象（user, product, zone, fuel_rate）
        target_id: 目标对象ID（可选）
        description: 操作描述（可选）
    """
    try:
        # 获取用户信息
        user_id = current_user.id if current_user.is_authenticated else None
        username = current_user.username if current_user.is_authenticated else None
        
        # 获取请求信息
        ip_address = request.remote_addr
        user_agent = request.user_agent.string
        method = request.method
        path = request.path
        
        # 创建日志记录
        log = Log(
            user_id=user_id,
            username=username,
            operation_type=operation_type,
            target_type=target_type,
            target_id=target_id,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            method=method,
            path=path,
            created_at=datetime.utcnow()
        )
        
        db.session.add(log)
        db.session.commit()
        
        # 开发环境下打印日志
        if current_app.debug:
            print(f'[Operation Log] {username} {operation_type} {target_type} {target_id}: {description}')
            
    except Exception as e:
        current_app.logger.error(f'Failed to log operation: {str(e)}')

# 创建全局logger实例
logger = Logger() 