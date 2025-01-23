import logging
from flask import Blueprint, current_app, request, jsonify
from flask_login import login_required, current_user
from app.models.product import Product
from app.utils.exceptions import ValidationError, ResourceNotFoundError
from app.extensions import db
from app.decorators import admin_required
from datetime import datetime
import pandas as pd
import os
from werkzeug.utils import secure_filename
from app.utils.excel_import import ExcelImporter
import traceback
import json
import tempfile

bp = Blueprint('products', __name__, url_prefix='/products')
logger = logging.getLogger(__name__)

@bp.route('', methods=['GET'])
@login_required
def get_products():
    """获取产品列表"""
    try:
        products = Product.query.order_by(Product.created_at.desc()).all()
        products_data = [product.to_dict() for product in products]
        logger.info(f'成功获取产品列表，共{len(products_data)}条记录')
        return jsonify({
            'success': True,
            'message': '获取产品列表成功',
            'data': products_data
        })
    except Exception as e:
        logger.error(f"获取产品列表失败: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'获取产品列表失败: {str(e)}'
        })

@bp.route('/<int:id>', methods=['GET'])
@login_required
def get_product(id):
    """获取产品详情"""
    try:
        product = Product.query.get(id)
        if not product:
            raise ResourceNotFoundError(f'产品不存在: {id}')
            
        return jsonify(product.to_dict())
    except ResourceNotFoundError as e:
        logger.warning(str(e))
        return jsonify({'message': str(e)}), 404
    except Exception as e:
        logger.error(f"获取产品详情失败: {str(e)}", exc_info=True)
        return jsonify({'message': '获取产品详情失败'}), 500

@bp.route('', methods=['POST'])
@login_required
@admin_required
def create_product():
    """创建产品"""
    try:
        data = request.get_json()
        if not data:
            raise ValidationError('无效的请求数据')
            
        # 验证必填字段
        required_fields = ['name', 'start_date']
        for field in required_fields:
            if not data.get(field):
                raise ValidationError(f'缺少必填字段: {field}')
        
        # 设置默认值
        if 'is_active' not in data:
            data['is_active'] = True
                
        # 创建产品
        product = Product()
        product.from_dict(data)
        
        db.session.add(product)
        db.session.commit()
        
        logger.info(f"创建产品成功: {product.id}")
        return jsonify(product.to_dict()), 201
        
    except ValidationError as e:
        logger.warning(f"创建产品验证错误: {str(e)}")
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        logger.error(f"创建产品失败: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({'message': '创建产品失败'}), 500

@bp.route('/<int:id>', methods=['PUT'])
@login_required
@admin_required
def update_product(id):
    """更新产品"""
    try:
        product = Product.query.get(id)
        if not product:
            raise ResourceNotFoundError(f'产品不存在: {id}')
            
        data = request.get_json()
        if not data:
            raise ValidationError('无效的请求数据')
            
        product.from_dict(data)
        db.session.commit()
        
        logger.info(f"更新产品成功: {id}")
        return jsonify(product.to_dict())
        
    except ResourceNotFoundError as e:
        logger.warning(str(e))
        return jsonify({'message': str(e)}), 404
    except ValidationError as e:
        logger.warning(f"更新产品验证错误: {str(e)}")
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        logger.error(f"更新产品失败: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({'message': '更新产品失败'}), 500

@bp.route('/<int:id>', methods=['DELETE'])
@login_required
@admin_required
def delete_product(id):
    """删除产品"""
    try:
        product = Product.query.get(id)
        if not product:
            raise ResourceNotFoundError(f'产品不存在: {id}')
            
        db.session.delete(product)
        db.session.commit()
        
        logger.info(f"删除产品成功: {id}")
        return '', 204
        
    except ResourceNotFoundError as e:
        logger.warning(str(e))
        return jsonify({'message': str(e)}), 404
    except Exception as e:
        logger.error(f"删除产品失败: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({'message': '删除产品失败'}), 500

@bp.route('/import', methods=['POST'])
@login_required
@admin_required
def import_product():
    try:
        if 'file' not in request.files:
            return jsonify({'error': '没有上传文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400
            
        if not file.filename.endswith('.xlsx'):
            return jsonify({'error': '请上传Excel文件'}), 400

        # 保存临时文件
        temp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        filename = secure_filename(file.filename)
        temp_path = os.path.join(temp_dir, filename)
        file.save(temp_path)

        # 读取所有sheet
        current_app.logger.info(f'开始读取Excel文件: {filename}')
        df_dict = pd.read_excel(temp_path, sheet_name=None)
        current_app.logger.info(f'Excel文件包含以下sheet: {list(df_dict.keys())}')
        
        # 将每个DataFrame转换为字符串格式
        result = []
        # 设置pandas显示选项
        pd.set_option('display.max_columns', None)        # 显示所有列
        pd.set_option('display.width', None)             # 不限制显示宽度
        pd.set_option('display.max_rows', None)          # 显示所有行
        pd.set_option('display.max_colwidth', None)      # 不限制列宽
        pd.set_option('display.expand_frame_repr', False) # 不换行显示
        pd.set_option('display.unicode.ambiguous_as_wide', True)  # 处理中文对齐
        pd.set_option('display.unicode.east_asian_width', True)   # 处理中文对齐
        pd.set_option('display.float_format', lambda x: '%.4f' % x if pd.notnull(x) else '')  # 统一数字格式化
        
        for sheet_name, df in df_dict.items():
            current_app.logger.info(f'处理sheet: {sheet_name}, 行数: {len(df)}')
            
            # 计算每列的最大宽度
            max_lengths = {}
            for col in df.columns:
                # 计算最大宽度（考虑中文字符）
                max_lengths[col] = max(
                    len(str(col)),
                    df[col].astype(str).apply(lambda x: sum(2 if ord(c) > 127 else 1 for c in str(x))).max()
                )
            
            # 格式化输出
            formatted_df = df.to_string(
                index=True,
                justify='right',
                col_space=max_lengths,
                max_colwidth=None,  # 不限制列宽
                na_rep='',
                max_rows=None,      # 显示所有行
                max_cols=None       # 显示所有列
            )
            
            result.append(f"{sheet_name}\n{formatted_df}\n")
            current_app.logger.info(f'sheet {sheet_name} 转换完成')

        # 删除临时文件
        os.remove(temp_path)
        current_app.logger.info('临时文件已删除')

        return jsonify({
            'message': '成功读取Excel文件',
            'data': '\n\n'.join(result)
        }), 200

    except Exception as e:
        current_app.logger.error(f'导入产品失败: {str(e)}')
        current_app.logger.error(traceback.format_exc())  # 添加详细的错误堆栈
        # 确保临时文件被删除
        try:
            if 'temp_path' in locals():
                os.remove(temp_path)
        except:
            pass
        return jsonify({'error': f'导入产品失败: {str(e)}'}), 500

@bp.route('/batch-import', methods=['POST'])
def batch_import_products():
    """批量导入产品"""
    try:
        logger.info('开始批量导入产品')
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': '没有接收到数据'})
            
        logger.info(f'接收到的数据: {str(data)[:200]}...')  # 只打印前200个字符避免日志过长
        
        # 查找包含费率数据的sheet（通常是Sheet2）
        lines = data.split('\n')
        current_sheet = None
        rate_data = []
        
        for line in lines:
            if line.startswith('Sheet'):
                current_sheet = line.strip()
                continue
                
            if current_sheet == 'Sheet2' and line.strip():
                # 解析费率行
                parts = line.split()
                if len(parts) >= 8 and parts[0].isdigit():  # 确保是数据行
                    try:
                        rate_row = {
                            'weight': int(parts[0]),
                            'Zone2': float(parts[2]),
                            'Zone3': float(parts[3]),
                            'Zone4': float(parts[4]),
                            'Zone5': float(parts[5]),
                            'Zone6': float(parts[6]),
                            'Zone7': float(parts[7]),
                            'Zone8': float(parts[8]) if len(parts) > 8 else 0.0
                        }
                        rate_data.append(rate_row)
                    except (ValueError, IndexError) as e:
                        logger.warning(f'跳过无效行: {line}, 错误: {str(e)}')
                        continue
        
        if not rate_data:
            return jsonify({
                'success': False,
                'message': '未找到有效的费率数据'
            })
            
        # 构建zone_rates数据
        zone_rates = []
        for rate in rate_data:
            zone_rate = {
                'weight': rate['weight']
            }
            # 添加各个区域的费率
            for zone in range(2, 9):
                zone_rate[str(zone)] = rate[f'Zone{zone}']
            zone_rates.append(zone_rate)
            
        # 创建新产品记录
        product = Product(
            name='FEDEX GROUND',  # 默认产品名
            carrier='FEDEX',  # 默认运营商
            unit='LB',  # 默认重量单位
            status='active',  # 设置状态为激活
            start_date=datetime.utcnow(),
            zone_rates=json.dumps(zone_rates)  # 保存区域费率
        )
        
        db.session.add(product)
        db.session.commit()
        
        logger.info(f'产品导入成功，ID: {product.id}')
        return jsonify({
            'success': True,
            'message': '导入成功',
            'data': {
                'id': product.id,
                'name': product.name
            }
        })
        
    except Exception as e:
        logger.error(f'导入失败: {str(e)}', exc_info=True)
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'导入失败: {str(e)}'
        })

@bp.route('/validate-rates/<int:id>', methods=['GET'])
@login_required
@admin_required
def validate_rates(id):
    """验证产品费率表数据"""
    try:
        logger.info(f'开始验证产品 {id} 的费率表')
        
        product = Product.query.get_or_404(id)
        logger.info(f'找到产品: {product.name}')
        
        is_valid = product.validate_zone_rates()
        logger.info(f'费率表验证结果: {"通过" if is_valid else "失败"}')
        
        return jsonify({
            'success': True,
            'message': '费率表验证完成',
            'is_valid': is_valid
        })
    except Exception as e:
        logger.error(f'验证费率表失败: {str(e)}', exc_info=True)
        return jsonify({
            'success': False,
            'message': f'验证费率表失败: {str(e)}'
        }), 500

@bp.route('/import-rates/<int:id>', methods=['POST'])
@login_required
@admin_required
def import_rates(id):
    """导入产品费率表"""
    try:
        logger.info(f'开始导入产品 {id} 的费率表')
        
        # 检查文件
        if 'file' not in request.files:
            logger.warning('未找到上传的文件')
            return jsonify({'success': False, 'message': '请选择Excel文件'})
            
        file = request.files['file']
        if not file or not file.filename:
            logger.warning('文件名为空')
            return jsonify({'success': False, 'message': '请选择文件'})
            
        if not file.filename.endswith(('.xlsx', '.xls')):
            logger.warning(f'文件格式错误: {file.filename}')
            return jsonify({'success': False, 'message': '请选择正确的Excel文件格式(.xlsx或.xls)'})

        # 获取产品
        product = Product.query.get_or_404(id)
        logger.info(f'找到产品: {product.name}')
        
        # 保存文件到临时路径
        temp_path = os.path.join(tempfile.gettempdir(), secure_filename(file.filename))
        file.save(temp_path)
        logger.info(f'文件已保存到临时目录: {temp_path}')
        
        try:
            # 导入Excel文件
            importer = ExcelImporter(temp_path)
            result = importer.process_excel()
            logger.info('Excel文件处理完成')
            
            # 更新产品费率
            product.zone_rates = json.dumps(result['zone_rates'], ensure_ascii=False)
            product.surcharges = json.dumps(result['surcharges'], ensure_ascii=False)
            product.volume_weight_factor = result['product_info']['dim']
            product.unit = result['product_info']['unit']
            
            db.session.commit()
            logger.info('产品费率更新成功')
            
            return jsonify({
                'success': True,
                'message': '导入成功',
                'data': product.to_dict()
            })
            
        except Exception as e:
            db.session.rollback()
            logger.error(f'处理Excel文件失败: {str(e)}', exc_info=True)
            return jsonify({
                'success': False,
                'message': f'处理Excel文件失败: {str(e)}'
            })
        finally:
            # 删除临时文件
            if os.path.exists(temp_path):
                os.remove(temp_path)
                logger.info('临时文件已删除')
                
    except Exception as e:
        logger.error(f'导入费率表失败: {str(e)}', exc_info=True)
        return jsonify({
            'success': False,
            'message': f'导入失败: {str(e)}'
        })