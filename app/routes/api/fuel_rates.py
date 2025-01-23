import logging
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models.fuel_rate import FuelRate
from app.utils.exceptions import ValidationError, ResourceNotFoundError, BusinessError
from app.extensions import db
from app.decorators import admin_required
from datetime import datetime, date

bp = Blueprint('fuel_rates', __name__, url_prefix='/fuel-rates')
logger = logging.getLogger(__name__)

@bp.route('', methods=['GET'])
@login_required
def get_fuel_rates():
    """获取燃油费率列表"""
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        active_only = request.args.get('active_only', '').lower() == 'true'
        
        # 验证分页参数
        if page < 1:
            raise ValidationError('页码必须大于0')
        if per_page < 1:
            raise ValidationError('每页数量必须大于0')
            
        # 构建查询
        rates_query = FuelRate.query
        
        # 日期过滤
        if start_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d').date()
                rates_query = rates_query.filter(FuelRate.effective_date >= start)
            except ValueError:
                raise ValidationError('无效的开始日期格式')
                
        if end_date:
            try:
                end = datetime.strptime(end_date, '%Y-%m-%d').date()
                rates_query = rates_query.filter(FuelRate.effective_date <= end)
            except ValueError:
                raise ValidationError('无效的结束日期格式')
                
        # 状态过滤
        if active_only:
            rates_query = rates_query.filter_by(is_active=True)
            
        # 分页
        pagination = rates_query.order_by(FuelRate.effective_date.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        rates = [rate.to_dict() for rate in pagination.items]
        logger.debug(f"获取燃油费率列表成功，数量: {len(rates)}")
        
        return jsonify({
            'fuel_rates': rates,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        })
        
    except ValidationError as e:
        logger.warning(f"获取燃油费率列表验证错误: {str(e)}")
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        logger.error(f"获取燃油费率列表失败: {str(e)}", exc_info=True)
        return jsonify({'message': '获取燃油费率列表失败'}), 500

@bp.route('/<int:id>', methods=['GET'])
@login_required
def get_fuel_rate(id):
    """获取燃油费率详情"""
    try:
        rate = FuelRate.query.get(id)
        if not rate:
            raise ResourceNotFoundError(f'燃油费率不存在: {id}')
            
        logger.debug(f"获取燃油费率详情成功: {id}")
        return jsonify(rate.to_dict())
        
    except ResourceNotFoundError as e:
        logger.warning(str(e))
        return jsonify({'message': str(e)}), 404
    except Exception as e:
        logger.error(f"获取燃油费率详情失败: {str(e)}", exc_info=True)
        return jsonify({'message': '获取燃油费率详情失败'}), 500

@bp.route('', methods=['POST'])
@login_required
@admin_required
def create_fuel_rate():
    """创建燃油费率"""
    try:
        data = request.get_json()
        if not data:
            raise ValidationError('无效的请求数据')
            
        # 验证必填字段
        required_fields = ['effective_date', 'rate']
        for field in required_fields:
            if not data.get(field):
                raise ValidationError(f'缺少必填字段: {field}')
                
        # 验证生效日期
        try:
            effective_date = datetime.strptime(data['effective_date'], '%Y-%m-%d')
        except ValueError:
            raise ValidationError('无效的日期格式')
            
        # 验证失效日期（如果提供）
        expiry_date = None
        if data.get('expiry_date'):
            try:
                expiry_date = datetime.strptime(data['expiry_date'], '%Y-%m-%d')
                if expiry_date <= effective_date:
                    raise ValidationError('失效日期必须晚于生效日期')
            except ValueError:
                raise ValidationError('无效的失效日期格式')
            
        # 验证费率
        try:
            rate = float(data['rate'])
            if rate < 0:
                raise ValueError
        except ValueError:
            raise ValidationError('费率必须是非负数')
            
        # 检查日期是否已存在
        if FuelRate.query.filter(
            FuelRate.effective_date <= effective_date,
            db.or_(
                FuelRate.expiry_date.is_(None),
                FuelRate.expiry_date >= effective_date
            )
        ).first():
            raise BusinessError('该日期范围内已存在燃油费率')
            
        # 创建燃油费率
        fuel_rate = FuelRate(
            effective_date=effective_date,
            expiry_date=expiry_date,
            rate=rate,
            is_active=data.get('is_active', True),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        db.session.add(fuel_rate)
        db.session.commit()
        
        logger.info(f"创建燃油费率成功: {fuel_rate.id}")
        return jsonify({
            'message': '创建成功',
            'fuel_rate': fuel_rate.to_dict()
        }), 201
        
    except ValidationError as e:
        logger.warning(f"创建燃油费率验证错误: {str(e)}")
        return jsonify({'message': str(e)}), 400
    except BusinessError as e:
        logger.warning(f"创建燃油费率业务错误: {str(e)}")
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        logger.error(f"创建燃油费率失败: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({'message': '创建燃油费率失败'}), 500

@bp.route('/<int:id>', methods=['PUT'])
@login_required
@admin_required
def update_fuel_rate(id):
    """更新燃油费率"""
    try:
        rate = FuelRate.query.get(id)
        if not rate:
            raise ResourceNotFoundError(f'燃油费率不存在: {id}')
            
        data = request.get_json()
        if not data:
            raise ValidationError('无效的请求数据')
            
        # 验证生效日期
        if 'effective_date' in data:
            try:
                effective_date = datetime.strptime(data['effective_date'], '%Y-%m-%d')
                
                # 只有当日期发生变化时才检查重叠
                if effective_date != rate.effective_date:
                    # 检查日期是否已被其他记录使用
                    existing = FuelRate.query.filter(
                        FuelRate.effective_date <= effective_date,
                        db.or_(
                            FuelRate.expiry_date.is_(None),
                            FuelRate.expiry_date >= effective_date
                        ),
                        FuelRate.id != id
                    ).first()
                    if existing:
                        raise BusinessError('该日期范围内已存在燃油费率')
                    
                rate.effective_date = effective_date
            except ValueError:
                raise ValidationError('无效的日期格式')
                
        # 验证失效日期
        if 'expiry_date' in data:
            if data['expiry_date']:
                try:
                    expiry_date = datetime.strptime(data['expiry_date'], '%Y-%m-%d')
                    if expiry_date <= rate.effective_date:
                        raise ValidationError('失效日期必须晚于生效日期')
                    rate.expiry_date = expiry_date
                except ValueError:
                    raise ValidationError('无效的失效日期格式')
            else:
                rate.expiry_date = None
                
        # 验证费率
        if 'rate' in data:
            try:
                rate_value = float(data['rate'])
                if rate_value < 0:
                    raise ValueError
                rate.rate = rate_value
            except ValueError:
                raise ValidationError('费率必须是非负数')
                
        # 更新启用状态
        if 'is_active' in data:
            rate.is_active = bool(data['is_active'])
                
        rate.updated_at = datetime.now()
        db.session.commit()
        
        logger.info(f"更新燃油费率成功: {id}")
        return jsonify({
            'message': '更新成功',
            'fuel_rate': rate.to_dict()
        })
        
    except ResourceNotFoundError as e:
        logger.warning(str(e))
        return jsonify({'message': str(e)}), 404
    except ValidationError as e:
        logger.warning(f"更新燃油费率验证错误: {str(e)}")
        return jsonify({'message': str(e)}), 400
    except BusinessError as e:
        logger.warning(f"更新燃油费率业务错误: {str(e)}")
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        logger.error(f"更新燃油费率失败: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({'message': '更新燃油费率失败'}), 500

@bp.route('/<int:id>', methods=['DELETE'])
@login_required
@admin_required
def delete_fuel_rate(id):
    """删除燃油费率"""
    try:
        rate = FuelRate.query.get(id)
        if not rate:
            raise ResourceNotFoundError(f'燃油费率不存在: {id}')
            
        db.session.delete(rate)
        db.session.commit()
        
        logger.info(f"删除燃油费率成功: {id}")
        return '', 204
        
    except ResourceNotFoundError as e:
        logger.warning(str(e))
        return jsonify({'message': str(e)}), 404
    except Exception as e:
        logger.error(f"删除燃油费率失败: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({'message': '删除燃油费率失败'}), 500

@bp.route('/check', methods=['POST'])
@login_required
def check_fuel_rate():
    """检查指定日期的燃油费率"""
    try:
        data = request.get_json()
        if not data:
            raise ValidationError('无效的请求数据')
            
        # 验证必填字段
        if 'date' not in data:
            raise ValidationError('缺少日期')
            
        # 验证日期格式
        try:
            check_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        except ValueError:
            raise ValidationError('无效的日期格式')
            
        # 查找生效的燃油费率
        rate = FuelRate.query.filter(
            FuelRate.effective_date <= check_date,
            FuelRate.is_active == True
        ).order_by(FuelRate.effective_date.desc()).first()
        
        if not rate:
            raise BusinessError('未找到生效的燃油费率')
            
        logger.debug(f"检查燃油费率成功: {check_date} -> {rate.id}")
        return jsonify({
            'date': data['date'],
            'fuel_rate': rate.to_dict()
        })
        
    except ValidationError as e:
        logger.warning(f"检查燃油费率验证错误: {str(e)}")
        return jsonify({'message': str(e)}), 400
    except BusinessError as e:
        logger.warning(f"检查燃油费率业务错误: {str(e)}")
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        logger.error(f"检查燃油费率失败: {str(e)}", exc_info=True)
        return jsonify({'message': '检查燃油费率失败'}), 500

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