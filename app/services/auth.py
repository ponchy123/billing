from datetime import datetime
from app import db
from app.models import User
from app.utils.exceptions import AuthError
from app.utils.email import send_email
from flask import current_app, render_template
import jwt
from time import time

class AuthService:
    """认证服务类"""
    
    @classmethod
    def authenticate_user(cls, username, password):
        """
        验证用户登录
        
        参数:
            username: 用户名
            password: 密码
        返回:
            User: 用户对象
        抛出:
            AuthError: 认证失败
        """
        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            raise AuthError('用户名或密码错误')
        if not user.is_active:
            raise AuthError('账号已被禁用')
        return user
    
    @classmethod
    def register_user(cls, username, email, password):
        """
        注册新用户
        
        参数:
            username: 用户名
            email: 邮箱
            password: 密码
        返回:
            User: 新创建的用户对象
        抛出:
            AuthError: 注册失败
        """
        if User.query.filter_by(username=username).first():
            raise AuthError('用户名已存在')
        if User.query.filter_by(email=email).first():
            raise AuthError('邮箱已被注册')
            
        user = User(username=username, email=email)
        user.password = password
        db.session.add(user)
        db.session.commit()
        return user
    
    @classmethod
    def change_password(cls, user, old_password, new_password):
        """
        修改用户密码
        
        参数:
            user: 用户对象
            old_password: 旧密码
            new_password: 新密码
        抛出:
            AuthError: 修改失败
        """
        if not user.check_password(old_password):
            raise AuthError('原密码错误')
            
        user.password = new_password
        db.session.commit()
    
    @classmethod
    def reset_password(cls, user, new_password):
        """
        重置用户密码
        
        参数:
            user: 用户对象
            new_password: 新密码
        """
        user.password = new_password
        db.session.commit()
    
    @classmethod
    def update_last_login(cls, user):
        """
        更新用户最后登录时间
        
        参数:
            user: 用户对象
        """
        user.last_login_at = datetime.utcnow()
        db.session.commit()
    
    @classmethod
    def get_reset_password_token(cls, user, expires_in=600):
        """
        生成密码重置令牌
        
        参数:
            user: 用户对象
            expires_in: 过期时间（秒）
        返回:
            str: JWT令牌
        """
        return jwt.encode(
            {'reset_password': user.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )
    
    @classmethod
    def verify_reset_password_token(cls, token):
        """
        验证密码重置令牌
        
        参数:
            token: JWT令牌
        返回:
            User: 用户对象
        抛出:
            AuthError: 验证失败
        """
        try:
            id = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )['reset_password']
        except:
            raise AuthError('无效的重置令牌')
            
        user = User.query.get(id)
        if user is None:
            raise AuthError('用户不存在')
        return user
    
    @classmethod
    def send_password_reset_email(cls, user):
        """
        发送密码重置邮件
        
        参数:
            user: 用户对象
        """
        token = cls.get_reset_password_token(user)
        send_email(
            subject='重置您的密码',
            recipients=[user.email],
            text_body=render_template('email/reset_password.txt',
                                    user=user, token=token),
            html_body=render_template('email/reset_password.html',
                                    user=user, token=token)
        ) 