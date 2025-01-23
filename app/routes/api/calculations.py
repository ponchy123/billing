import logging
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models.calculation import Calculation
from app.models.product import Product
from app.models.postal_zone import PostalZone
from app.models.fuel_rate import FuelRate
from app.utils.exceptions import ValidationError, ResourceNotFoundError, BusinessError
from app.extensions import db
from datetime import datetime

bp = Blueprint('calculations', __name__)
logger = logging.getLogger(__name__)

@bp.route('/calculations', methods=['GET'])
@login_required
def get_calculations():
    """获取计算历史列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        query = request.args.get('query', '')
        
        # 验证分页参数
        if page < 1:
            raise ValidationError('页码必须大于0')
        if per_page < 1:
            raise ValidationError('每页数量必须大于0')
            
        # 构建查询
        calculations_query = Calculation.query
        
        # 权限过滤
        if not current_user.is_admin:
            calculations_query = calculations_query.filter_by(user_id=current_user.id)
            
        # 搜索过滤
        if query:
            calculations_query = calculations_query.join(Product).filter(
                db.or_(
                    Product.name.ilike(f'%{query}%'),
                    Product.code.ilike(f'%{query}%')
                )
            )
            
        # 日期范围过滤
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if start_date:
            try:
                start_date = datetime.fromisoformat(start_date)
                calculations_query = calculations_query.filter(Calculation.created_at >= start_date)
            except ValueError:
                raise ValidationError('无效的开始日期格式，请使用ISO格式(YYYY-MM-DD)')
                
        if end_date:
            try:
                end_date = datetime.fromisoformat(end_date)
                calculations_query = calculations_query.filter(Calculation.created_at <= end_date)
            except ValueError:
                raise ValidationError('无效的结束日期格式，请使用ISO格式(YYYY-MM-DD)')
                
        # 分页
        pagination = calculations_query.order_by(Calculation.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        calculations = []
        for calc in pagination.items:
            calc_dict = calc.to_dict()
            calc_dict['product'] = calc.product.to_dict() if calc.product else None
            calculations.append(calc_dict)
            
        logger.debug(f"获取计算历史列表成功，数量: {len(calculations)}")
        
        return jsonify({
            'calculations': calculations,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        })
        
    except ValidationError as e:
        logger.warning(f"获取计算历史列表验证错误: {str(e)}")
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        logger.error(f"获取计算历史列表失败: {str(e)}", exc_info=True)
        return jsonify({'message': '获取计算历史列表失败'}), 500

@bp.route('/calculations/<int:id>', methods=['GET'])
@login_required
def get_calculation(id):
    """获取计算历史详情"""
    try:
        calculation = Calculation.query.get(id)
        if not calculation:
            raise ResourceNotFoundError(f'计算历史不存在: {id}')
            
        # 权限检查
        if not current_user.is_admin and calculation.user_id != current_user.id:
            raise BusinessError('无权访问此计算历史')
            
        calc_dict = calculation.to_dict()
        calc_dict['product'] = calculation.product.to_dict() if calculation.product else None
        
        logger.debug(f"获取计算历史详情成功: {id}")
        return jsonify(calc_dict)
        
    except ResourceNotFoundError as e:
        logger.warning(str(e))
        return jsonify({'message': str(e)}), 404
    except BusinessError as e:
        logger.warning(f"获取计算历史详情业务错误: {str(e)}")
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        logger.error(f"获取计算历史详情失败: {str(e)}", exc_info=True)
        return jsonify({'message': '获取计算历史详情失败'}), 500

@bp.route('/calculations', methods=['POST'])
@login_required
def create_calculation():
    """创建计算"""
    try:
        data = request.get_json()
        if not data:
            raise ValidationError('无效的请求数据')
            
        # 验证必填字段
        required_fields = ['product_id', 'length', 'width', 'height', 'weight', 'postal_code']
        for field in required_fields:
            if not data.get(field):
                raise ValidationError(f'缺少必填字段: {field}')
                
        # 验证产品
        product = Product.query.get(data['product_id'])
        if not product:
            raise ValidationError('产品不存在')
        if not product.is_active:
            raise BusinessError('产品已停用')
            
        # 验证尺寸和重量
        try:
            length = float(data['length'])
            width = float(data['width'])
            height = float(data['height'])
            weight = float(data['weight'])
            
            if any(v <= 0 for v in [length, width, height, weight]):
                raise ValueError
        except ValueError:
            raise ValidationError('尺寸和重量必须是大于0的数字')
            
        # 验证邮编
        postal_code = data['postal_code'].strip()
        if not postal_code.isdigit() or len(postal_code) != 6:
            raise ValidationError('无效的邮政编码格式')
            
        # 获取分区
        postal_zone = PostalZone.query.filter(
            PostalZone.start_code <= postal_code,
            PostalZone.end_code >= postal_code
        ).first()
        if not postal_zone:
            raise BusinessError('不支持的邮政编码')
            
        # 获取当前燃油费率
        fuel_rate = FuelRate.query.filter(
            FuelRate.effective_date <= datetime.now().date(),
            FuelRate.is_active == True
        ).order_by(FuelRate.effective_date.desc()).first()
        if not fuel_rate:
            raise BusinessError('当前没有可用的燃油费率')
            
        # 计算费用
        base_fee = product.base_fee
        zone_fee = base_fee * postal_zone.rate
        fuel_fee = base_fee * fuel_rate.rate
        
        # 创建计算记录
        calculation = Calculation(
            user_id=current_user.id,
            product_id=product.id,
            length=length,
            width=width,
            height=height,
            weight=weight,
            postal_code=postal_code,
            postal_zone_id=postal_zone.id,
            fuel_rate_id=fuel_rate.id,
            base_fee=base_fee,
            zone_fee=zone_fee,
            fuel_fee=fuel_fee,
            total_fee=base_fee + zone_fee + fuel_fee
        )
        
        db.session.add(calculation)
        db.session.commit()
        
        calc_dict = calculation.to_dict()
        calc_dict['product'] = product.to_dict()
        
        logger.info(f"创建计算成功: {calculation.id}")
        return jsonify({
            'message': '计算成功',
            'calculation': calc_dict
        }), 201
        
    except ValidationError as e:
        logger.warning(f"创建计算验证错误: {str(e)}")
        return jsonify({'message': str(e)}), 400
    except BusinessError as e:
        logger.warning(f"创建计算业务错误: {str(e)}")
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        logger.error(f"创建计算失败: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({'message': '创建计算失败'}), 500

# 错误处理器
@bp.errorhandler(ValidationError)
def handle_validation_error(e):
    """处理验证错误"""
    logger.warning(f"验证错误: {str(e)}")
    return jsonify({'message': str(e)}), 400

@bp.errorhandler(ResourceNotFoundError)
def handle_not_found_error(e):
    """处理资源不存在错误"""
    logger.warning(str(e))
    return jsonify({'message': str(e)}), 404

@bp.errorhandler(BusinessError)
def handle_business_error(e):
    """处理业务错误"""
    logger.warning(f"业务错误: {str(e)}")
    return jsonify({'message': str(e)}), 400

@bp.errorhandler(Exception)
def handle_unexpected_error(e):
    """处理未预期的错误"""
    logger.error(f"未预期的错误: {str(e)}", exc_info=True)
    return jsonify({'message': '服务器内部错误'}), 500 