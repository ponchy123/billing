import os
import sys
from flask_migrate import init, migrate, upgrade
from flask.cli import FlaskGroup

def init_database():
    """初始化数据库"""
    try:
        from app import create_app, db
        from app.config import Config
        
        print("创建应用实例...")
        app = create_app(Config)
        
        with app.app_context():
            print("检查数据库连接...")
            try:
                db.engine.connect()
                print("数据库连接成功！")
            except Exception as e:
                print(f"数据库连接失败: {str(e)}")
                sys.exit(1)
            
            print("开始数据库初始化...")
            
            # 确保migrations目录存在
            if not os.path.exists('migrations'):
                print("初始化数据库迁移...")
                init()
            
            print("生成迁移脚本...")
            migrate()
            
            print("应用迁移...")
            upgrade()
            
            print("数据库初始化完成！")
            
    except Exception as e:
        print(f"初始化过程出错: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    init_database() 