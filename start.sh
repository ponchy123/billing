#!/bin/bash

# 等待数据库启动
echo "Waiting for database..."
sleep 5

# 初始化数据库
echo "Initializing database..."
flask db init || true
flask db migrate || true
flask db upgrade || true

# 启动应用
echo "Starting application..."
gunicorn wsgi:app 