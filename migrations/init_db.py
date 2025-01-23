import os
import sys
from sqlalchemy import create_engine, text
from urllib.parse import urlparse
import time

def wait_for_db(db_url, max_retries=5):
    """等待数据库准备就绪"""
    parsed = urlparse(db_url)
    dbname = parsed.path[1:]
    user = parsed.username
    password = parsed.password
    host = parsed.hostname
    port = parsed.port or 5432

    retry_count = 0
    while retry_count < max_retries:
        try:
            print(f"尝试连接数据库... {retry_count + 1}/{max_retries}")
            print(f"连接信息: host={host}, port={port}, dbname={dbname}, user={user}")
            
            engine = create_engine(db_url)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("数据库连接成功！")
            return True
        except Exception as e:
            retry_count += 1
            print(f"连接失败: {str(e)}")
            if retry_count < max_retries:
                print(f"等待5秒后重试...")
                time.sleep(5)
    
    print("数据库连接失败！")
    return False

def init_database():
    """初始化数据库"""
    try:
        from app import create_app, db
        from app.config import Config
        
        print("\n=== 开始初始化数据库 ===")
        
        app = create_app(Config)
        
        with app.app_context():
            # 获取数据库URL
            db_url = app.config['SQLALCHEMY_DATABASE_URI']
            print(f"数据库URL: {db_url}")
            
            # 等待数据库就绪
            if not wait_for_db(db_url):
                print("无法连接到数据库，退出初始化")
                sys.exit(1)
            
            try:
                print("\n创建数据库表...")
                db.create_all()
                print("数据库表创建完成！")
                
            except Exception as e:
                print(f"创建数据库表失败: {str(e)}")
                sys.exit(1)
            
    except Exception as e:
        print(f"初始化过程出错: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    init_database() 