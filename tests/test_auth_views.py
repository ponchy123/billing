import unittest
from flask import url_for
from app import create_app, db
from app.models import User

class AuthViewsTestCase(unittest.TestCase):
    def setUp(self):
        """测试前的准备工作"""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        """测试后的清理工作"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_login_page(self):
        """测试登录页面"""
        response = self.client.get(url_for('auth.login'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('用户登录' in response.get_data(as_text=True))

    def test_register_page(self):
        """测试注册页面"""
        response = self.client.get(url_for('auth.register'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('用户注册' in response.get_data(as_text=True))

    def test_register_and_login(self):
        """测试注册和登录"""
        # 注册新用户
        response = self.client.post(url_for('auth.register'), data={
            'username': 'john',
            'email': 'john@example.com',
            'password': 'cat',
            'password2': 'cat',
            'role': 'customer',
            'company': 'Test Company',
            'contact': 'John',
            'phone': '12345678901',
            'address': 'Test Address'
        })
        self.assertEqual(response.status_code, 302)

        # 使用新注册的用户登录
        response = self.client.post(url_for('auth.login'), data={
            'username': 'john',
            'password': 'cat',
            'remember_me': False
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('登录成功' in response.get_data(as_text=True))

    def test_logout(self):
        """测试登出"""
        # 创建用户
        u = User(username='john', email='john@example.com', role='customer')
        u.password = 'cat'
        db.session.add(u)
        db.session.commit()

        # 登录
        self.client.post(url_for('auth.login'), data={
            'username': 'john',
            'password': 'cat',
            'remember_me': False
        })

        # 登出
        response = self.client.get(url_for('auth.logout'), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('您已退出登录' in response.get_data(as_text=True))

    def test_change_password(self):
        """测试修改密码"""
        # 创建用户
        u = User(username='john', email='john@example.com', role='customer')
        u.password = 'cat'
        db.session.add(u)
        db.session.commit()

        # 登录
        self.client.post(url_for('auth.login'), data={
            'username': 'john',
            'password': 'cat',
            'remember_me': False
        })

        # 修改密码
        response = self.client.post(url_for('auth.change_password'), data={
            'old_password': 'cat',
            'password': 'dog',
            'password2': 'dog'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('密码修改成功' in response.get_data(as_text=True))

        # 使用新密码登录
        response = self.client.post(url_for('auth.login'), data={
            'username': 'john',
            'password': 'dog',
            'remember_me': False
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('登录成功' in response.get_data(as_text=True)) 