from datetime import datetime

def format_date(date, format='%Y-%m-%d'):
    """
    格式化日期为字符串
    
    Args:
        date: datetime对象
        format: 日期格式字符串,默认为'%Y-%m-%d'
        
    Returns:
        str: 格式化后的日期字符串
    """
    if not date:
        return None
    return date.strftime(format)

def parse_date(date_str, format='%Y-%m-%d'):
    """
    解析日期字符串为datetime对象
    
    Args:
        date_str: 日期字符串
        format: 日期格式字符串,默认为'%Y-%m-%d'
        
    Returns:
        datetime: 解析后的datetime对象
        
    Raises:
        ValueError: 如果日期字符串格式不正确
    """
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, format)
    except ValueError:
        raise ValueError(f"日期格式不正确,应为{format}")

def is_valid_date(date_str, format='%Y-%m-%d'):
    """
    验证日期字符串是否有效
    
    Args:
        date_str: 日期字符串
        format: 日期格式字符串,默认为'%Y-%m-%d'
        
    Returns:
        bool: 日期字符串是否有效
    """
    if not date_str:
        return False
    try:
        datetime.strptime(date_str, format)
        return True
    except ValueError:
        return False 