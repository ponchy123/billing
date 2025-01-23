import logging
from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from app.decorators import admin_required
from app.utils.exceptions import PermissionDeniedError
from app.models.user import User
from app.models.product import Product
from app.models.postal_zone import PostalZone
from app.models.fuel_rate import FuelRate

bp = Blueprint('admin', __name__, url_prefix='/admin')
logger = logging.getLogger(__name__)

@bp.route('/stats')
@login_required
@admin_required
def get_stats():
    """获取统计数据"""
    try:
        # 获取各个模型的数量
        stats = {
            'users': User.query.count(),
            'products': Product.query.count(),
            'zones': PostalZone.query.count(),
            'rates': FuelRate.query.count()
        }
        
        logger.info('获取统计数据成功')
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"获取统计数据失败: {str(e)}", exc_info=True)
        return jsonify({'error': '获取统计数据失败'}), 500

@bp.route('/')
@login_required
@admin_required
def admin_index():
    """管理员首页"""
    try:
        logger.debug(f"管理员访问首页: {current_user.username}")
        return render_template('index.html')
    except Exception as e:
        logger.error(f"访问管理员首页失败: {str(e)}", exc_info=True)
        return jsonify({'error': '页面加载失败'}), 500

@bp.route('/products')
@login_required
@admin_required
def products():
    """产品管理页面"""
    try:
        logger.debug(f"管理员访问产品管理页面: {current_user.username}")
        return render_template('index.html')
    except Exception as e:
        logger.error(f"访问产品管理页面失败: {str(e)}", exc_info=True)
        return jsonify({'error': '页面加载失败'}), 500

@bp.route('/users')
@login_required
@admin_required
def users():
    """用户管理页面"""
    try:
        logger.debug(f"管理员访问用户管理页面: {current_user.username}")
        return render_template('index.html')
    except Exception as e:
        logger.error(f"访问用户管理页面失败: {str(e)}", exc_info=True)
        return jsonify({'error': '页面加载失败'}), 500

@bp.route('/postal-zones')
@login_required
@admin_required
def postal_zones():
    """邮政区域管理页面"""
    try:
        logger.debug(f"管理员访问邮政区域管理页面: {current_user.username}")
        return render_template('index.html')
    except Exception as e:
        logger.error(f"访问邮政区域管理页面失败: {str(e)}", exc_info=True)
        return jsonify({'error': '页面加载失败'}), 500

# 添加通配符路由，处理所有未匹配的管理路由
@bp.route('/<path:path>')
@login_required
@admin_required
def catch_all(path):
    """处理所有未匹配的管理路由"""
    try:
        logger.debug(f"管理员访问路径: {path}, 用户: {current_user.username}")
        return render_template('index.html')
    except Exception as e:
        logger.error(f"访问路径失败: {path}, 错误: {str(e)}", exc_info=True)
        return jsonify({'error': '页面加载失败'}), 500

# 错误处理器
@bp.errorhandler(PermissionDeniedError)
def handle_permission_denied(e):
    """处理权限不足错误"""
    logger.warning(f"权限不足: {str(e)}, 用户: {current_user.username if not current_user.is_anonymous else 'anonymous'}")
    return jsonify({'error': str(e)}), 403

@bp.errorhandler(Exception)
def handle_unexpected_error(e):
    """处理未预期的错误"""
    logger.error(f"未预期的错误: {str(e)}", exc_info=True)
    return jsonify({'error': '服务器内部错误'}), 500 