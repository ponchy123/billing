#!/bin/bash

# 设置环境变量
export FLASK_APP=wsgi.py
export FLASK_ENV=production
export PYTHONPATH=/opt/render/project/src

# 安装依赖
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install psycopg2-binary --no-cache-dir

# 等待数据库启动
echo "Waiting for database..."
sleep 15

# 启动应用
echo "Starting application..."
gunicorn "wsgi:app" \
    --workers=2 \
    --threads=4 \
    --worker-class=gthread \
    --worker-tmp-dir=/dev/shm \
    --log-level=debug \
    --timeout=120 \
    --preload 