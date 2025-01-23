from flask import Blueprint, render_template, current_app, send_from_directory
import os

bp = Blueprint('main', __name__)

@bp.route('/', defaults={'path': ''})
@bp.route('/<path:path>')
def catch_all(path):
    """处理所有前端路由请求"""
    current_app.logger.info(f'请求路径: {path}')
    
    # 如果是静态文件请求，尝试从静态目录提供文件
    if path.startswith('static/'):
        try:
            file_path = path.replace('static/', '', 1)
            return send_from_directory(current_app.static_folder, file_path)
        except Exception as e:
            current_app.logger.error(f'静态文件处理错误: {str(e)}')
            return render_template('index.html')
    
    # 其他所有路由都返回 index.html
    return render_template('index.html')