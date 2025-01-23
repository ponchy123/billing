import logging
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models.user import User
from app.utils.exceptions import ValidationError, ResourceNotFoundError, BusinessError
from app.extensions import db
from app.decorators import admin_required
from datetime import datetime
import re

bp = Blueprint('users', __name__, url_prefix='/users')
logger = logging.getLogger(__name__)

@bp.route('', methods=['GET'])
@login_required
@admin_required
def get_users():
    """获取用户列表"""
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        query = request.args.get('query', '')
        role = request.args.get('role', '')
        status = request.args.get('status', '')
        
        # 验证分页参数
        if page < 1:
            raise ValidationError('页码必须大于0')
        if per_page < 1:
            raise ValidationError('每页数量必须大于0')
            
        # 构建查询
        users_query = User.query
        
        # 搜索过滤
        if query:
            users_query = users_query.filter(
                db.or_(
                    User.username.ilike(f'%{query}%'),
                    User.email.ilike(f'%{query}%')
                )
            )
            
        # 角色过滤
        if role:
            users_query = users_query.filter_by(role=role)
            
        # 状态过滤
        if status:
            is_active = (status == 'active')
            users_query = users_query.filter_by(is_active=is_active)
            
        # 分页
        pagination = users_query.order_by(User.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        users = [user.to_dict() for user in pagination.items]
        logger.debug(f"获取用户列表成功，数量: {len(users)}")
        
        return jsonify({
            'users': users,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        })
        
    except ValidationError as e:
        logger.warning(f"获取用户列表验证错误: {str(e)}")
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        logger.error(f"获取用户列表失败: {str(e)}", exc_info=True)
        return jsonify({'message': '获取用户列表失败'}), 500

@bp.route('/<int:id>', methods=['GET'])
@login_required
def get_user(id):
    """获取用户详情"""
    try:
        # 权限检查
        if not current_user.is_admin and current_user.id != id:
            raise BusinessError('无权访问此用户信息')
            
        user = User.query.get(id)
        if not user:
            raise ResourceNotFoundError(f'用户不存在: {id}')
            
        logger.debug(f"获取用户详情成功: {id}")
        return jsonify(user.to_dict())
        
    except ResourceNotFoundError as e:
        logger.warning(str(e))
        return jsonify({'message': str(e)}), 404
    except BusinessError as e:
        logger.warning(f"获取用户详情业务错误: {str(e)}")
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        logger.error(f"获取用户详情失败: {str(e)}", exc_info=True)
        return jsonify({'message': '获取用户详情失败'}), 500

@bp.route('/<int:id>', methods=['PUT'])
@login_required
def update_user(id):
    """更新用户信息"""
    try:
        # 权限检查
        if not current_user.is_admin and current_user.id != id:
            raise BusinessError('无权修改此用户信息')
            
        user = User.query.get(id)
        if not user:
            raise ResourceNotFoundError(f'用户不存在: {id}')
            
        data = request.get_json()
        if not data:
            raise ValidationError('无效的请求数据')
            
        # 验证邮箱
        if 'email' in data:
            email = data['email']
            if not email:
                raise ValidationError('邮箱不能为空')
                
            # 验证邮箱格式
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                raise ValidationError('无效的邮箱格式')
                
            # 检查邮箱是否已被使用
            if User.query.filter(User.id != id, User.email == email).first():
                raise BusinessError('邮箱已被使用')
                
            user.email = email
            
        # 验证密码
        if 'password' in data:
            password = data['password']
            if not password:
                raise ValidationError('密码不能为空')
                
            # 验证密码强度
            if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$', password):
                raise ValidationError('密码必须至少8位，包含字母和数字')
                
            user.set_password(password)
            
        # 管理员可以修改其他字段
        if current_user.is_admin:
            if 'role' in data:
                role = data['role']
                if role not in ['admin', 'customer']:
                    raise ValidationError('无效的角色值')
                user.role = role
                
            if 'is_active' in data:
                is_active = data['is_active']
                if not isinstance(is_active, bool):
                    raise ValidationError('无效的状态值')
                user.is_active = is_active
                
        user.updated_at = datetime.now()
        db.session.commit()
        
        logger.info(f"更新用户信息成功: {id}")
        return jsonify({
            'message': '更新成功',
            'user': user.to_dict()
        })
        
    except ResourceNotFoundError as e:
        logger.warning(str(e))
        return jsonify({'message': str(e)}), 404
    except ValidationError as e:
        logger.warning(f"更新用户信息验证错误: {str(e)}")
        return jsonify({'message': str(e)}), 400
    except BusinessError as e:
        logger.warning(f"更新用户信息业务错误: {str(e)}")
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        logger.error(f"更新用户信息失败: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({'message': '更新用户信息失败'}), 500

@bp.route('/<int:id>/activate', methods=['POST'])
@login_required
@admin_required
def activate_user(id):
    """激活用户"""
    try:
        user = User.query.get(id)
        if not user:
            raise ResourceNotFoundError(f'用户不存在: {id}')
            
        if user.is_active:
            raise BusinessError('用户已处于激活状态')
            
        user.is_active = True
        user.updated_at = datetime.now()
        db.session.commit()
        
        logger.info(f"激活用户成功: {id}")
        return jsonify({
            'message': '激活成功',
            'user': user.to_dict()
        })
        
    except ResourceNotFoundError as e:
        logger.warning(str(e))
        return jsonify({'message': str(e)}), 404
    except BusinessError as e:
        logger.warning(f"激活用户业务错误: {str(e)}")
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        logger.error(f"激活用户失败: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({'message': '激活用户失败'}), 500

@bp.route('/<int:id>/deactivate', methods=['POST'])
@login_required
@admin_required
def deactivate_user(id):
    """禁用用户"""
    try:
        user = User.query.get(id)
        if not user:
            raise ResourceNotFoundError(f'用户不存在: {id}')
            
        if user.id == current_user.id:
            raise BusinessError('不能禁用自己的账号')
            
        if not user.is_active:
            raise BusinessError('用户已处于禁用状态')
            
        user.is_active = False
        user.updated_at = datetime.now()
        db.session.commit()
        
        logger.info(f"禁用用户成功: {id}")
        return jsonify({
            'message': '禁用成功',
            'user': user.to_dict()
        })
        
    except ResourceNotFoundError as e:
        logger.warning(str(e))
        return jsonify({'message': str(e)}), 404
    except BusinessError as e:
        logger.warning(f"禁用用户业务错误: {str(e)}")
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        logger.error(f"禁用用户失败: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({'message': '禁用用户失败'}), 500

# 错误处理器
@bp.errorhandler(ValidationError)
def handle_validation_error(e):
    """处理验证错误"""
    logger.warning(f"验证错误: {str(e)}")
    return jsonify({'message': str(e)}), 400

@bp.errorhandler(ResourceNotFoundError)
def handle_not_found_error(e):
    """处理资源不存在错误"""
    logger.warning(str(e))
    return jsonify({'message': str(e)}), 404

@bp.errorhandler(BusinessError)
def handle_business_error(e):
    """处理业务错误"""
    logger.warning(f"业务错误: {str(e)}")
    return jsonify({'message': str(e)}), 400

@bp.errorhandler(Exception)
def handle_unexpected_error(e):
    """处理未预期的错误"""
    logger.error(f"未预期的错误: {str(e)}", exc_info=True)
    return jsonify({'message': '服务器内部错误'}), 500 