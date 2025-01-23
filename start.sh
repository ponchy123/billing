#!/bin/bash

# 设置环境变量
export FLASK_APP=wsgi.py
export FLASK_ENV=production
export PYTHONPATH=/opt/render/project/src

# 安装依赖
echo "Installing dependencies..."
pip install -r requirements.txt
pip install psycopg2-binary --no-cache-dir

# 等待数据库启动
echo "Waiting for database..."
sleep 10

# 初始化数据库
echo "Initializing database..."
python migrations/init_db.py
if [ $? -ne 0 ]; then
    echo "Database initialization failed!"
    exit 1
fi

# 启动应用
echo "Starting application..."
gunicorn wsgi:app --log-level debug --timeout 120 