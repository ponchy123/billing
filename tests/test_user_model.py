import unittest
from app import create_app, db
from app.models import User

class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        """测试前的准备工作"""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        """测试后的清理工作"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        """测试密码设置"""
        u = User(password='cat')
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        """测试密码不可读"""
        u = User(password='cat')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        """测试密码验证"""
        u = User(password='cat')
        self.assertTrue(u.verify_password('cat'))
        self.assertFalse(u.verify_password('dog'))

    def test_password_salts_are_random(self):
        """测试密码加密盐值是随���的"""
        u = User(password='cat')
        u2 = User(password='cat')
        self.assertTrue(u.password_hash != u2.password_hash)

    def test_valid_reset_token(self):
        """测试有效的重置密码令牌"""
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.get_reset_password_token()
        self.assertTrue(User.verify_reset_password_token(token) == u)

    def test_invalid_reset_token(self):
        """测试无效的重置密码令牌"""
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.get_reset_password_token()
        db.session.delete(u)
        db.session.commit()
        self.assertFalse(User.verify_reset_password_token(token) is not None)

    def test_user_role(self):
        """测试用户角色"""
        u = User(username='john', email='john@example.com', role='admin')
        self.assertTrue(u.is_admin())
        self.assertFalse(u.is_service())
        self.assertFalse(u.is_customer())

        u.role = 'service'
        self.assertFalse(u.is_admin())
        self.assertTrue(u.is_service())
        self.assertFalse(u.is_customer())

        u.role = 'customer'
        self.assertFalse(u.is_admin())
        self.assertFalse(u.is_service())
        self.assertTrue(u.is_customer()) 