import os
from flask import current_app
from flask_migrate import Migrate, upgrade, init, migrate, stamp
from alembic.config import Config
from alembic import command
from ..models import db

class MigrationService:
    """数据库迁移服务类"""
    
    def __init__(self, app=None):
        self.app = app
        self.migrate = None
        if app is not None:
            self.init_app(app)
            
    def init_app(self, app):
        """初始化迁移"""
        self.app = app
        self.migrate = Migrate(app, db)
        
        # 创建迁移目录
        migrations_dir = os.path.join(app.root_path, 'migrations')
        if not os.path.exists(migrations_dir):
            os.makedirs(migrations_dir)
            
    def init_migrations(self):
        """初始化迁移环境"""
        try:
            with self.app.app_context():
                # 初始化迁移目录
                init()
                
                # 创建初始迁移
                migrate()
                
                # 标记为最新版本
                stamp('head')
                
            return True, "迁移环境初始化成功"
            
        except Exception as e:
            return False, f"迁移环境初始化失败: {str(e)}"
            
    def create_migration(self, message=None):
        """创建新的迁移"""
        try:
            with self.app.app_context():
                migrate(message=message)
                
            return True, "迁移创建成功"
            
        except Exception as e:
            return False, f"迁移创建失败: {str(e)}"
            
    def upgrade_database(self, target='head'):
        """升级数据库"""
        try:
            with self.app.app_context():
                upgrade(target)
                
            return True, "数据库升级成功"
            
        except Exception as e:
            return False, f"数据库升级失败: {str(e)}"
            
    def downgrade_database(self, target):
        """降级数据库"""
        try:
            with self.app.app_context():
                command.downgrade(self._get_config(), target)
                
            return True, "数据库降级成功"
            
        except Exception as e:
            return False, f"数据库降级失败: {str(e)}"
            
    def get_current_revision(self):
        """获取当前版本"""
        try:
            with self.app.app_context():
                config = self._get_config()
                return command.current(config)
                
        except Exception as e:
            return None
            
    def get_history(self):
        """获取迁移历史"""
        try:
            with self.app.app_context():
                config = self._get_config()
                return command.history(config)
                
        except Exception as e:
            return None
            
    def _get_config(self):
        """获取Alembic配置"""
        config = Config()
        config.set_main_option('script_location', os.path.join(self.app.root_path, 'migrations'))
        config.set_main_option('sqlalchemy.url', self.app.config['SQLALCHEMY_DATABASE_URI'])
        return config 