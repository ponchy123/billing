import os
import sys
from sqlalchemy import create_engine, text
from app import create_app, db
from app.config import Config

# 创建应用实例
app = create_app(Config)

# 初始化数据库
with app.app_context():
    try:
        # 获取数据库URL
        db_url = app.config['SQLALCHEMY_DATABASE_URI']
        print(f"数据库URL: {db_url}")
        
        # 创建引擎
        engine = create_engine(db_url)
        
        # 测试连接
        with engine.connect() as conn:
            conn.execute(text('SELECT 1'))
        print("数据库连接成功！")
        
        # 创建所有表
        print("创建数据库表...")
        db.create_all()
        print("数据库表创建完成！")
        
    except Exception as e:
        print(f"数据库初始化失败: {str(e)}")
        if not app.debug:
            sys.exit(1)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True) 