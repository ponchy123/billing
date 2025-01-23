import os
import sys
import time
import psycopg2
from urllib.parse import urlparse

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
            conn = psycopg2.connect(
                dbname=dbname,
                user=user,
                password=password,
                host=host,
                port=port
            )
            conn.close()
            print("数据库连接成功！")
            return True
        except psycopg2.OperationalError as e:
            retry_count += 1
            print(f"等待数据库就绪... 尝试 {retry_count}/{max_retries}")
            time.sleep(5)
    
    print("数据库连接失败！")
    return False

def init_database():
    """初始化数据库"""
    try:
        from app import create_app, db
        from app.config import Config
        
        app = create_app(Config)
        
        with app.app_context():
            db_url = app.config['SQLALCHEMY_DATABASE_URI']
            print(f"数据库URL: {db_url}")
            
            if not wait_for_db(db_url):
                sys.exit(1)
            
            print("创建数据库表...")
            db.create_all()
            print("数据库表创建完成！")
            
    except Exception as e:
        print(f"初始化失败: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    init_database() 