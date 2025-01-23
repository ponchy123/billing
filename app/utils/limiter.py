from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

def init_app(app):
    """初始化限流器"""
    limiter.init_app(app)
    
    # 自定义错误处理
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return {
            'error': 'ratelimit_error',
            'message': '请求过于频繁，请稍后再试'
        }, 429 