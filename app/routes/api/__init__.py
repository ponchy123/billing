from flask import Blueprint
from . import auth, users, products, postal_zones, fuel_rates, calculator, admin

# 创建主API蓝图
bp = Blueprint('api', __name__, url_prefix='/api')

# 注册子模块路由
bp.register_blueprint(postal_zones.bp, url_prefix='/postal-zones')
bp.register_blueprint(auth.bp)
bp.register_blueprint(users.bp)
bp.register_blueprint(products.bp)
bp.register_blueprint(fuel_rates.bp)
bp.register_blueprint(calculator.bp)
bp.register_blueprint(admin.bp, url_prefix='/admin')  # 添加 url_prefix 