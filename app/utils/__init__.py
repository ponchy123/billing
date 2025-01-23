from functools import wraps
from flask import jsonify, abort
from flask_login import current_user
from .paginate import paginate

def login_required(f):
    """登录验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({
                'message': '请先登录'
            }), 401
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """管理员权限装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def permission_required(permission):
    """权限验证装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return jsonify({
                    'message': '请先登录'
                }), 401
            if permission not in current_user.get_permissions():
                return jsonify({
                    'message': '权限不足'
                }), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator 

__all__ = ['paginate'] 