from typing import Tuple, Any, Optional, Dict, List
from functools import wraps
from flask import jsonify, current_app
from werkzeug.exceptions import HTTPException
from .utils.exceptions import (
    BusinessError,
    AuthError,
    ValidationError,
    ResourceNotFoundError,
    PermissionDeniedError,
    ResourceConflictError,
    RateLimitError
)

class ErrorHandlers:
    """错误处理工具类"""
    
    # HTTP状态码
    HTTP_400_BAD_REQUEST = 400
    HTTP_401_UNAUTHORIZED = 401
    HTTP_403_FORBIDDEN = 403
    HTTP_404_NOT_FOUND = 404
    HTTP_500_INTERNAL_SERVER_ERROR = 500
    
    @staticmethod
    def format_error_response(error_code: str, message: str, status_code: int) -> Tuple[Dict, int]:
        """格式化错误响应"""
        return jsonify({
            'error': error_code,
            'message': message
        }), status_code
    
    @staticmethod
    def handle_validation(func):
        """验证函数装饰器"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                current_app.logger.exception(e)
                return False, f"验证失败: {str(e)}"
        return wrapper
    
    @staticmethod
    def handle_db_operation(func):
        """数据库操作装饰器"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                return True, result
            except Exception as e:
                current_app.logger.exception(e)
                return False, f"数据库操作失败: {str(e)}"
        return wrapper
    
    @staticmethod
    def handle_file_operation(func):
        """文件操作装饰器"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                return True, result
            except Exception as e:
                current_app.logger.exception(e)
                return False, f"文件操作失败: {str(e)}"
        return wrapper
    
    @staticmethod
    def handle_calculation(func):
        """计算函数装饰器"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                return True, result
            except Exception as e:
                current_app.logger.exception(e)
                return False, f"计算失败: {str(e)}"
        return wrapper

def register_error_handlers(app):
    """注册错误处理器"""
    
    @app.errorhandler(BusinessError)
    def handle_business_error(e):
        return ErrorHandlers.format_error_response(e.code, e.message, 400)
    
    @app.errorhandler(AuthError)
    def handle_auth_error(e):
        return ErrorHandlers.format_error_response(e.code, e.message, 401)
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        return ErrorHandlers.format_error_response(e.code, e.message, 400)
    
    @app.errorhandler(ResourceNotFoundError)
    def handle_not_found_error(e):
        return ErrorHandlers.format_error_response(e.code, e.message, 404)
    
    @app.errorhandler(PermissionDeniedError)
    def handle_permission_denied_error(e):
        return ErrorHandlers.format_error_response(e.code, e.message, 403)
    
    @app.errorhandler(ResourceConflictError)
    def handle_resource_conflict_error(e):
        return ErrorHandlers.format_error_response(e.code, e.message, 409)
    
    @app.errorhandler(RateLimitError)
    def handle_rate_limit_error(e):
        return ErrorHandlers.format_error_response(e.code, e.message, 429)
    
    @app.errorhandler(400)
    def bad_request(e):
        return ErrorHandlers.format_error_response('BAD_REQUEST', str(e), 400)
    
    @app.errorhandler(401)
    def unauthorized(e):
        return ErrorHandlers.format_error_response('UNAUTHORIZED', '请先登录', 401)
    
    @app.errorhandler(403)
    def forbidden(e):
        return ErrorHandlers.format_error_response('FORBIDDEN', '权限不足', 403)
    
    @app.errorhandler(404)
    def not_found(e):
        return ErrorHandlers.format_error_response('NOT_FOUND', '资源不存在', 404)
    
    @app.errorhandler(405)
    def method_not_allowed(e):
        return ErrorHandlers.format_error_response('METHOD_NOT_ALLOWED', '不支持的请求方法', 405)
    
    @app.errorhandler(429)
    def too_many_requests(e):
        return ErrorHandlers.format_error_response('TOO_MANY_REQUESTS', '请求过于频繁，请稍后再试', 429)
    
    @app.errorhandler(500)
    def internal_server_error(e):
        app.logger.error(f'Server Error: {str(e)}')
        return ErrorHandlers.format_error_response('INTERNAL_SERVER_ERROR', '服务器内部错误', 500)
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(e):
        app.logger.exception('An unexpected error has occurred.')
        return ErrorHandlers.format_error_response('INTERNAL_SERVER_ERROR', '服务器内部错误', 500) 