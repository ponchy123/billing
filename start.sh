#!/bin/bash

# 设置环境变量
export FLASK_APP=wsgi.py
export FLASK_ENV=production
export PYTHONPATH=/opt/render/project/src

# 安装依赖
echo "Installing dependencies..."
python -m pip install --upgrade pip
pip install wheel setuptools
pip install psycopg2-binary==2.9.9 --no-cache-dir
pip install -r requirements.txt

# 初始化数据库
echo "Initializing database..."
python migrations/init_db.py
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