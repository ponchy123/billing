class BusinessError(Exception):
    """业务逻辑异常基类"""
    def __init__(self, message, code=None):
        super().__init__(message)
        self.message = message
        self.code = code or 'BUSINESS_ERROR'

class AuthError(BusinessError):
    """认证相关异常"""
    def __init__(self, message, code=None):
        super().__init__(message, code or 'AUTH_ERROR')

class ValidationError(BusinessError):
    """数据验证异常"""
    def __init__(self, message, code=None):
        super().__init__(message, code or 'VALIDATION_ERROR')

class ResourceNotFoundError(BusinessError):
    """资源不存在异常"""
    def __init__(self, message, code=None):
        super().__init__(message, code or 'NOT_FOUND_ERROR')

class PermissionDeniedError(BusinessError):
    """权限不足异常"""
    def __init__(self, message, code=None):
        super().__init__(message, code or 'PERMISSION_DENIED')

class ResourceConflictError(BusinessError):
    """资源冲突异常"""
    def __init__(self, message, code=None):
        super().__init__(message, code or 'RESOURCE_CONFLICT')

class RateLimitError(BusinessError):
    """请求频率限制异常"""
    def __init__(self, message, code=None):
        super().__init__(message, code or 'RATE_LIMIT_ERROR')

class EmailError(BusinessError):
    """邮件相关异常"""
    def __init__(self, message, code=None):
        super().__init__(message, code or 'EMAIL_ERROR')

class ExportError(BusinessError):
    """导出相关异常"""
    def __init__(self, message, code=None):
        super().__init__(message, code or 'EXPORT_ERROR') 