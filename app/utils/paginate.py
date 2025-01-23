from flask import request

def paginate(query, page=None, per_page=None):
    """
    对查询结果进行分页
    
    Args:
        query: SQLAlchemy查询对象
        page: 页码(从1开始)
        per_page: 每页记录数
        
    Returns:
        Pagination: 分页对象
    """
    if page is None:
        page = request.args.get('page', 1, type=int)
    if per_page is None:
        per_page = request.args.get('per_page', 10, type=int)
        
    # 限制每页记录数的范围
    if per_page > 100:
        per_page = 100
    elif per_page < 1:
        per_page = 10
        
    return query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    ) 