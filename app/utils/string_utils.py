import re

def truncate_string(s, length=100, suffix='...'):
    """
    截断字符串
    
    Args:
        s: 要截断的字符串
        length: 最大长度,默认为100
        suffix: 截断后添加的后缀,默认为'...'
        
    Returns:
        str: 截断后的字符串
    """
    if not s:
        return ''
    s = str(s)
    if len(s) <= length:
        return s
    return s[:length] + suffix

def is_valid_email(email):
    """
    验证邮箱格式是否有效
    
    Args:
        email: 邮箱地址
        
    Returns:
        bool: 邮箱格式是否有效
    """
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def is_valid_postcode(postcode):
    """
    验证邮编格式是否有效
    
    Args:
        postcode: 邮编
        
    Returns:
        bool: 邮编格式是否有效
    """
    if not postcode:
        return False
    pattern = r'^\d{5}$'  # 5位数字
    return bool(re.match(pattern, str(postcode)))

def is_valid_username(username):
    """
    验证用户名格式是否有效
    
    Args:
        username: 用户名
        
    Returns:
        bool: 用户名格式是否有效
    """
    if not username:
        return False
    pattern = r'^[a-zA-Z0-9_]{4,20}$'  # 4-20位字母、数字、下划线
    return bool(re.match(pattern, username))

def is_valid_password(password):
    """
    验证密码格式是否有效
    
    Args:
        password: 密码
        
    Returns:
        bool: 密码格式是否有效
    """
    if not password:
        return False
    # 至少8位,包含大小写字母、数字
    pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$'
    return bool(re.match(pattern, password)) 