import os
from flask_migrate import init, migrate, upgrade
from app import create_app, db
from app.config import Config

def init_database():
    """初始化数据库"""
    app = create_app(Config)
    
    with app.app_context():
        # 确保migrations目录存在
        if not os.path.exists('migrations'):
            print("初始化数据库迁移...")
            init()
        
        print("生成迁移脚本...")
        migrate()
        
        print("应用迁移...")
        upgrade()
        
        print("数据库初始化完成！")

if __name__ == '__main__':
    init_database() 