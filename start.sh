#!/bin/bash

# 设置环境变量
export FLASK_APP=wsgi.py
export FLASK_ENV=production
export PYTHONPATH=/opt/render/project/src

# 安装依赖
echo "Installing dependencies..."
pip install --upgrade pip
pip install psycopg2-binary --no-cache-dir
pip install -r requirements.txt

# 初始化数据库
echo "Initializing database..."
python init.py
if [ $? -ne 0 ]; then
    echo "Database initialization failed!"
    exit 1
fi

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