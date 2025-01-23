import os
import shutil
from werkzeug.utils import secure_filename

def ensure_dir(directory):
    """
    确保目录存在,如果不存在则创建
    
    Args:
        directory: 目录路径
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

def get_file_extension(filename):
    """
    获取文件扩展名
    
    Args:
        filename: 文件名
        
    Returns:
        str: 文件扩展名(不包含点号)
    """
    if not filename:
        return ''
    return os.path.splitext(filename)[1][1:].lower()

def is_allowed_file(filename, allowed_extensions):
    """
    检查文件类型是否允许
    
    Args:
        filename: 文件名
        allowed_extensions: 允许的扩展名集合
        
    Returns:
        bool: 文件类型是否允许
    """
    if not filename:
        return False
    return get_file_extension(filename) in allowed_extensions

def safe_filename(filename):
    """
    生成安全的文件名
    
    Args:
        filename: 原始文件名
        
    Returns:
        str: 安全的文件名
    """
    if not filename:
        return ''
    return secure_filename(filename)

def remove_file(filepath):
    """
    安全删除文件
    
    Args:
        filepath: 文件路径
        
    Returns:
        bool: 是否删除成功
    """
    try:
        if os.path.isfile(filepath):
            os.remove(filepath)
            return True
    except OSError:
        pass
    return False

def copy_file(src, dst):
    """
    复制文件
    
    Args:
        src: 源文件路径
        dst: 目标文件路径
        
    Returns:
        bool: 是否复制成功
    """
    try:
        shutil.copy2(src, dst)
        return True
    except OSError:
        return False

def get_file_size(filepath):
    """
    获取文件大小(字节)
    
    Args:
        filepath: 文件路径
        
    Returns:
        int: 文件大小(字节),如果文件不存在则返回0
    """
    try:
        return os.path.getsize(filepath)
    except OSError:
        return 0 