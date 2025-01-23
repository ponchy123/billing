import logging
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.decorators import admin_required
from app.models.user import User
from app.extensions import db
from app.utils.exceptions import ValidationError, BusinessError
from datetime import datetime

bp = Blueprint('admin', __name__)
logger = logging.getLogger(__name__)

@bp.route('/users', methods=['GET', 'POST'])
@login_required
@admin_required
def users():
    """用户管理"""
    if request.method == 'GET':
        try:
            users = User.query.all()
            return jsonify({
                'success': True,
                'data': [user.to_dict() for user in users]
            })
        except Exception as e:
            logger.error(f"获取用户列表失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': '获取用户列表失败'
            }), 500
    elif request.method == 'POST':
        try:
            data = request.get_json()
            if not data:
                raise ValidationError('无效的请求数据')
                
            # 验证必填字段
            required_fields = ['username', 'email', 'password', 'role']
            for field in required_fields:
                if not data.get(field):
                    raise ValidationError(f'缺少必填字段: {field}')
                    
            # 检查用户名是否已存在
            if User.query.filter_by(username=data['username']).first():
                raise BusinessError('用户名已存在')
                
            # 检查邮箱是否已存在
            if User.query.filter_by(email=data['email']).first():
                raise BusinessError('邮箱已被注册')
                
            # 创建新用户
            user = User(
                username=data['username'],
                email=data['email'],
                role=data['role'],
                active=True,
                created_at=datetime.now()
            )
            user.set_password(data['password'])
            
            db.session.add(user)
            db.session.commit()
            
            logger.info(f"管理员 {current_user.username} 创建了新用户: {user.username}")
            return jsonify({
                'success': True,
                'message': '用户创建成功',
                'data': user.to_dict()
            })
            
        except ValidationError as e:
            logger.warning(f"创建用户验证错误: {str(e)}")
            return jsonify({
                'success': False,
                'message': str(e)
            }), 400
        except BusinessError as e:
            logger.warning(f"创建用户业务错误: {str(e)}")
            return jsonify({
                'success': False,
                'message': str(e)
            }), 400
        except Exception as e:
            logger.error(f"创建用户失败: {str(e)}")
            db.session.rollback()
            return jsonify({
                'success': False,
                'message': '创建用户失败'
            }), 500

@bp.route('/users/<int:user_id>', methods=['PUT', 'DELETE'])
@login_required
@admin_required
def user(user_id):
    """用户操作"""
    if request.method == 'PUT':
        try:
            user = User.query.get(user_id)
            if not user:
                raise BusinessError('用户不存在')
                
            data = request.get_json()
            if not data:
                raise ValidationError('无效的请求数据')
                
            # 更新用户信息
            if 'username' in data:
                # 检查新用户名是否与其他用户重复
                existing_user = User.query.filter_by(username=data['username']).first()
                if existing_user and existing_user.id != user_id:
                    raise BusinessError('用户名已存在')
                user.username = data['username']
                
            if 'email' in data:
                # 检查新邮箱是否与其他用户重复
                existing_user = User.query.filter_by(email=data['email']).first()
                if existing_user and existing_user.id != user_id:
                    raise BusinessError('邮箱已被注册')
                user.email = data['email']
                
            if 'role' in data:
                user.role = data['role']
                
            if 'active' in data:
                user.active = data['active']
                
            if 'password' in data:
                user.set_password(data['password'])
                
            user.updated_at = datetime.now()
            db.session.commit()
            
            logger.info(f"管理员 {current_user.username} 更新了用户 {user.username} 的信息")
            return jsonify({
                'success': True,
                'message': '用户信息更新成功',
                'data': user.to_dict()
            })
            
        except ValidationError as e:
            logger.warning(f"更新用户验证错误: {str(e)}")
            return jsonify({
                'success': False,
                'message': str(e)
            }), 400
        except BusinessError as e:
            logger.warning(f"更新用户业务错误: {str(e)}")
            return jsonify({
                'success': False,
                'message': str(e)
            }), 400
        except Exception as e:
            logger.error(f"更新用户失败: {str(e)}")
            db.session.rollback()
            return jsonify({
                'success': False,
                'message': '更新用户失败'
            }), 500
    elif request.method == 'DELETE':
        try:
            user = User.query.get(user_id)
            if not user:
                raise BusinessError('用户不存在')
                
            # 不允许删除自己
            if user.id == current_user.id:
                raise BusinessError('不能删除当前登录的用户')
                
            db.session.delete(user)
            db.session.commit()
            
            logger.info(f"管理员 {current_user.username} 删除了用户 {user.username}")
            return jsonify({
                'success': True,
                'message': '用户删除成功'
            })
            
        except BusinessError as e:
            logger.warning(f"删除用户业务错误: {str(e)}")
            return jsonify({
                'success': False,
                'message': str(e)
            }), 400
        except Exception as e:
            logger.error(f"删除用户失败: {str(e)}")
            db.session.rollback()
            return jsonify({
                'success': False,
                'message': '删除用户失败'
            }), 500 