import os
import logging
import json
import mimetypes
from logging.handlers import RotatingFileHandler
from flask import Flask, request, jsonify, render_template, send_from_directory, url_for
from flask_cors import CORS
from config import Config
from app.extensions import db, login_manager, migrate, init_extensions
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# 初始化扩展
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    """创建Flask应用"""
    print("\n=== 开始创建应用 ===")
    
    # 创建Flask应用实例
    app = Flask(__name__,
                static_folder='static',
                static_url_path='/static',
                template_folder='templates')
    
    # 加载配置
    app.config.from_object(config_class)
    config_class.init_app(app)
    
    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    
    # 配置日志
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/app.log',
                                         maxBytes=10240,
                                         backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('应用启动')
    
    # 注册蓝图
    from app.routes.api import bp as api_bp
    from app.routes.main import bp as main_bp
    from app.routes.admin import bp as admin_bp
    
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(main_bp)
    
    # 错误处理
    @app.errorhandler(404)
    def not_found_error(error):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Not found', 'path': request.path}), 404
        return render_template('index.html'), 200
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Internal server error'}), 500
        return render_template('index.html'), 200
    
    # 静态文件处理
    @app.route('/static/<path:filename>')
    def serve_static(filename):
        """处理静态文件请求"""
        app.logger.info(f'处理静态文件请求: {filename}')
        try:
            return send_from_directory(app.static_folder, filename)
        except Exception as e:
            app.logger.error(f'静态文件处理错误: {str(e)}')
            return jsonify({'error': 'Static file not found'}), 404
    
    # 开发环境的 Vite HMR 请求处理
    @app.route('/@vite/client')
    def vite_client():
        """处理 Vite HMR 客户端请求"""
        if app.debug:
            return '', 204
        return '', 404
    
    # 配置静态文件MIME类型
    mimetypes.add_type('application/javascript', '.js')
    mimetypes.add_type('text/javascript', '.js')
    mimetypes.add_type('text/css', '.css')
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    
    # 自定义静态文件处理
    @app.route('/static/js/<path:filename>')
    def serve_js(filename):
        response = send_from_directory(
            os.path.join(app.root_path, 'static', 'js'),
            filename,
            mimetype='application/javascript'
        )
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers['Content-Type'] = 'application/javascript'
        return response

    @app.route('/static/css/<path:filename>')
    def serve_css(filename):
        response = send_from_directory(
            os.path.join(app.root_path, 'static', 'css'),
            filename,
            mimetype='text/css'
        )
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers['Content-Type'] = 'text/css'
        return response
    
    @app.route('/static/js/<path:filename>.vue')
    def serve_vue(filename):
        return send_from_directory(
            os.path.join(app.root_path, 'static', 'js'),
            f"{filename}.vue",
            mimetype='application/javascript'
        )
    
    # 添加正确的 MIME 类型
    app.config['MIME_TYPES'] = {
        '.js': 'application/javascript',
        '.mjs': 'application/javascript',
        '.css': 'text/css',
        '.html': 'text/html'
    }
    
    @app.after_request
    def add_header(response):
        if response.mimetype == 'application/javascript':
            response.headers['Content-Type'] = 'application/javascript; charset=utf-8'
        return response
    
    return app 