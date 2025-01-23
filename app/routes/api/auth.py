import logging
from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app.utils.exceptions import ValidationError, BusinessError
from app.extensions import db
from datetime import datetime
import re

bp = Blueprint('auth', __name__, url_prefix='/auth')
logger = logging.getLogger(__name__)

@bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        if not data:
            raise ValidationError('无效的请求数据')
            
        # 验证必填字段
        required_fields = ['username', 'password']
        for field in required_fields:
            if not data.get(field):
                raise ValidationError(f'缺少必填字段: {field}')
                
        username = data['username']
        password = data['password']
        
        # 查找用户
        user = User.query.filter_by(username=username).first()
        if not user:
            raise BusinessError('用户名或密码错误')
            
        # 验证密码
        if not user.check_password(password):
            logger.warning(f"用户密码错误: {username}")
            raise BusinessError('用户名或密码错误')
            
        # 验证用户状态
        if not user.active:
            raise BusinessError('账号已被禁用')
            
        # 登录用户并生成令牌
        login_user(user)
        token = user.generate_token()
        
        # 打印调试信息
        logger.info(f"用户登录成功: {username}, 角色: {user.role}, 是否管理员: {user.is_admin}")
        
        return jsonify({
            'message': '登录成功',
            'token': token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'is_admin': user.is_admin,
                'active': user.active,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'updated_at': user.updated_at.isoformat() if user.updated_at else None
            }
        })
        
    except ValidationError as e:
        logger.warning(f"登录验证错误: {str(e)}")
        return jsonify({'message': str(e)}), 400
    except BusinessError as e:
        logger.warning(f"登录业务错误: {str(e)}")
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        logger.error(f"登录失败: {str(e)}", exc_info=True)
        return jsonify({'message': '登录失败'}), 500

@bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """用户登出"""
    try:
        username = current_user.username
        logout_user()
        
        logger.info(f"用户登出成功: {username}")
        return jsonify({'message': '登出成功'})
        
    except Exception as e:
        logger.error(f"登出失败: {str(e)}", exc_info=True)
        return jsonify({'message': '登出失败'}), 500

@bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.get_json()
        if not data:
            raise ValidationError('无效的请求数据')
            
        # 验证必填字段
        required_fields = ['username', 'password', 'email']
        for field in required_fields:
            if not data.get(field):
                raise ValidationError(f'缺少必填字段: {field}')
                
        username = data['username']
        password = data['password']
        email = data['email']
        
        # 验证用户名格式
        if not re.match(r'^[a-zA-Z0-9_]{4,20}$', username):
            raise ValidationError('用户名必须是4-20位字母、数字或下划线')
            
        # 验证密码强度
        if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$', password):
            raise ValidationError('密码必须至少8位，包含字母和数字')
            
        # 验证邮箱格式
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValidationError('无效的邮箱格式')
            
        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            raise BusinessError('用户名已存在')
            
        # 检查邮箱是否已存在
        if User.query.filter_by(email=email).first():
            raise BusinessError('邮箱已被注册')
            
        # 创建用户
        user = User(
            username=username,
            email=email,
            role='customer',
            is_active=True,
            created_at=datetime.now()
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        logger.info(f"用户注册成功: {username}")
        return jsonify({
            'message': '注册成功',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'is_active': user.is_active,
                'created_at': user.created_at.isoformat()
            }
        }), 201
        
    except ValidationError as e:
        logger.warning(f"注册验证错误: {str(e)}")
        return jsonify({'message': str(e)}), 400
    except BusinessError as e:
        logger.warning(f"注册业务错误: {str(e)}")
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        logger.error(f"注册失败: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({'message': '注册失败'}), 500

@bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """修改密码"""
    try:
        data = request.get_json()
        if not data:
            raise ValidationError('无效的请求数据')
            
        # 验证必填字段
        required_fields = ['old_password', 'new_password']
        for field in required_fields:
            if not data.get(field):
                raise ValidationError(f'缺少必填字段: {field}')
                
        old_password = data['old_password']
        new_password = data['new_password']
        
        # 验证旧密码
        if not current_user.check_password(old_password):
            raise BusinessError('旧密码错误')
            
        # 验证新密码强度
        if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$', new_password):
            raise ValidationError('新密码必须至少8位，包含字母和数字')
            
        # 修改密码
        current_user.set_password(new_password)
        db.session.commit()
        
        logger.info(f"用户修改密码成功: {current_user.username}")
        return jsonify({'message': '密码修改成功'})
        
    except ValidationError as e:
        logger.warning(f"修改密码验证错误: {str(e)}")
        return jsonify({'message': str(e)}), 400
    except BusinessError as e:
        logger.warning(f"修改密码业务错误: {str(e)}")
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        logger.error(f"修改密码失败: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({'message': '修改密码失败'}), 500

@bp.route('/reset-password', methods=['POST'])
def reset_password():
    """重置密码"""
    try:
        data = request.get_json()
        if not data:
            raise ValidationError('无效的请求数据')
            
        # 验证必填字段
        required_fields = ['email']
        for field in required_fields:
            if not data.get(field):
                raise ValidationError(f'缺少必填字段: {field}')
                
        email = data['email']
        
        # 验证邮箱格式
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValidationError('无效的邮箱格式')
            
        # 查找用户
        user = User.query.filter_by(email=email).first()
        if not user:
            raise BusinessError('邮箱未注册')
            
        # TODO: 发送重置密码邮件
        
        logger.info(f"用户请求重置密码: {email}")
        return jsonify({'message': '重置密码邮件已发送'})
        
    except ValidationError as e:
        logger.warning(f"重置密码验证错误: {str(e)}")
        return jsonify({'message': str(e)}), 400
    except BusinessError as e:
        logger.warning(f"重置密码业务错误: {str(e)}")
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        logger.error(f"重置密码失败: {str(e)}", exc_info=True)
        return jsonify({'message': '重置密码失败'}), 500

# 错误处理器
@bp.errorhandler(ValidationError)
def handle_validation_error(e):
    """处理验证错误"""
    logger.warning(f"验证错误: {str(e)}")
    return jsonify({'message': str(e)}), 400

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