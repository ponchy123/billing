from functools import wraps
from flask import abort
from flask_login import current_user

def admin_required(f):
    """管理员权限装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def calculator_required(f):
    """计算权限装饰器 - 所有已登录用户都可以访问"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def service_required(f):
    """客服权限装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        if not getattr(current_user, 'is_service', False):
            abort(403)
        return f(*args, **kwargs)
    return decorated_function 