from functools import wraps
from flask import current_app
from datetime import datetime, timedelta
import json

class CacheService:
    """缓存服务类"""
    
    def __init__(self, cache=None):
        self.cache = cache
        
    def init_app(self, app, cache):
        """初始化缓存"""
        self.cache = cache
        
    def cached(self, timeout=300, key_prefix='view'):
        """视图函数缓存装饰器"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                # 生成缓存键
                cache_key = self._make_cache_key(key_prefix, f.__name__, args, kwargs)
                
                # 尝试从缓存获取
                rv = self.cache.get(cache_key)
                if rv is not None:
                    return rv
                    
                # 执行函数
                rv = f(*args, **kwargs)
                
                # 存入缓存
                self.cache.set(cache_key, rv, timeout=timeout)
                return rv
                
            return decorated_function
        return decorator
        
    def _make_cache_key(self, key_prefix, func_name, args, kwargs):
        """生成缓存键"""
        key_parts = [key_prefix, func_name]
        
        # 添加位置参数
        for arg in args:
            if isinstance(arg, (int, float, str, bool)):
                key_parts.append(str(arg))
                
        # 添加关键字参数
        if kwargs:
            sorted_kwargs = sorted(kwargs.items())
            for k, v in sorted_kwargs:
                if isinstance(v, (int, float, str, bool)):
                    key_parts.append(f"{k}:{v}")
                    
        return ':'.join(key_parts)
        
    def cache_product(self, product_id, data, timeout=3600):
        """缓存产品信息"""
        key = f'product:{product_id}'
        self.cache.set(key, json.dumps(data), timeout=timeout)
        
    def get_cached_product(self, product_id):
        """获取缓存的产品信息"""
        key = f'product:{product_id}'
        data = self.cache.get(key)
        return json.loads(data) if data else None
        
    def invalidate_product_cache(self, product_id):
        """使产品缓存失效"""
        key = f'product:{product_id}'
        self.cache.delete(key)
        
    def cache_postcode(self, postcode, data, timeout=3600):
        """缓存邮编信息"""
        key = f'postcode:{postcode}'
        self.cache.set(key, json.dumps(data), timeout=timeout)
        
    def get_cached_postcode(self, postcode):
        """获取缓存的邮编信息"""
        key = f'postcode:{postcode}'
        data = self.cache.get(key)
        return json.loads(data) if data else None
        
    def invalidate_postcode_cache(self, postcode):
        """使邮编缓存失效"""
        key = f'postcode:{postcode}'
        self.cache.delete(key)
        
    def cache_calculation(self, input_hash, result, timeout=1800):
        """缓存计算结果"""
        key = f'calculation:{input_hash}'
        self.cache.set(key, json.dumps(result), timeout=timeout)
        
    def get_cached_calculation(self, input_hash):
        """获取缓存的计算结果"""
        key = f'calculation:{input_hash}'
        data = self.cache.get(key)
        return json.loads(data) if data else None
        
    def cache_fuel_rate(self, rate, timeout=3600):
        """缓存燃油费率"""
        self.cache.set('fuel_rate', rate, timeout=timeout)
        
    def get_cached_fuel_rate(self):
        """获取缓存的燃油费率"""
        return self.cache.get('fuel_rate')
        
    def invalidate_fuel_rate_cache(self):
        """使燃油费率缓存失效"""
        self.cache.delete('fuel_rate')
        
    def clear_all_cache(self):
        """清除所有缓存"""
        self.cache.clear() 