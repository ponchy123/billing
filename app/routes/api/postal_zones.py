import logging
from flask import Blueprint, current_app, request, jsonify
from flask_login import login_required, current_user
from app.models.postal_zone import PostalZone
from app.utils.exceptions import ValidationError, ResourceNotFoundError, BusinessError
from app.extensions import db
from app.decorators import admin_required
from datetime import datetime
import re
import pandas as pd
import os
import tempfile
from werkzeug.utils import secure_filename
import json

bp = Blueprint('postal_zones', __name__)
logger = logging.getLogger(__name__)

@bp.route('', methods=['GET'])
@login_required
def get_postal_zones():
    """获取邮政区域列表"""
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        query = request.args.get('query', '')
        active_only = request.args.get('active_only', '').lower() == 'true'
        
        # 验证分页参数
        if page < 1:
            raise ValidationError('页码必须大于0')
        if per_page < 1:
            raise ValidationError('每页数量必须大于0')
            
        # 构建查询
        zones_query = PostalZone.query
        
        # 搜索过滤
        if query:
            zones_query = zones_query.filter(
                db.or_(
                    PostalZone.code.ilike(f'%{query}%'),
                    PostalZone.name.ilike(f'%{query}%'),
                    PostalZone.description.ilike(f'%{query}%')
                )
            )
            
        # 状态过滤
        if active_only:
            zones_query = zones_query.filter_by(is_active=True)
            
        # 分页
        pagination = zones_query.order_by(PostalZone.code.asc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        zones = [zone.to_dict() for zone in pagination.items]
        logger.debug(f"获取邮政区域列表成功，数量: {len(zones)}")
        
        return jsonify({
            'postal_zones': zones,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        })
        
    except ValidationError as e:
        logger.warning(f"获取邮政区域列表验证错误: {str(e)}")
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        logger.error(f"获取邮政区域列表失败: {str(e)}", exc_info=True)
        return jsonify({'message': '获取邮政区域列表失败'}), 500

@bp.route('/<string:code>', methods=['GET'])
@login_required
def get_postal_zone(code):
    """获取邮政区域详情"""
    try:
        zone = PostalZone.query.filter_by(code=code).first()
        if not zone:
            raise ResourceNotFoundError(f'邮政区域不存在: {code}')
            
        logger.debug(f"获取邮政区域详情成功: {code}")
        return jsonify(zone.to_dict())
        
    except ResourceNotFoundError as e:
        logger.warning(str(e))
        return jsonify({'message': str(e)}), 404
    except Exception as e:
        logger.error(f"获取邮政区域详情失败: {str(e)}", exc_info=True)
        return jsonify({'message': '获取邮政区域详情失败'}), 500

@bp.route('', methods=['POST'])
@login_required
@admin_required
def create_postal_zone():
    """创建邮政区域"""
    try:
        data = request.get_json()
        if not data:
            raise ValidationError('无效的请求数据')
            
        # 验证必填字段
        required_fields = ['code', 'name', 'base_fee']
        for field in required_fields:
            if not data.get(field):
                raise ValidationError(f'缺少必填字段: {field}')
                
        # 验证区域代码格式
        code = data['code']
        if not re.match(r'^[A-Z0-9]{2,10}$', code):
            raise ValidationError('区域代码必须是2-10位大写字母或数字')
            
        # 检查区域代码是否已存在
        if PostalZone.query.filter_by(code=code).first():
            raise BusinessError(f'区域代码已存在: {code}')
            
        # 验证基础费用
        try:
            base_fee = float(data['base_fee'])
            if base_fee < 0:
                raise ValueError
        except ValueError:
            raise ValidationError('基础费用必须是非负数')
            
        # 创建邮政区域
        zone = PostalZone(
            code=code,
            name=data['name'],
            description=data.get('description', ''),
            base_fee=base_fee,
            is_active=data.get('is_active', True),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        db.session.add(zone)
        db.session.commit()
        
        logger.info(f"创建邮政区域成功: {code}")
        return jsonify({
            'message': '创建成功',
            'postal_zone': zone.to_dict()
        }), 201
        
    except ValidationError as e:
        logger.warning(f"创建邮政区域验证错误: {str(e)}")
        return jsonify({'message': str(e)}), 400
    except BusinessError as e:
        logger.warning(f"创建邮政区域业务错误: {str(e)}")
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        logger.error(f"创建邮政区域失败: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({'message': '创建邮政区域失败'}), 500

@bp.route('/<string:code>', methods=['PUT'])
@login_required
@admin_required
def update_postal_zone(code):
    """更新邮政区域"""
    try:
        zone = PostalZone.query.filter_by(code=code).first()
        if not zone:
            raise ResourceNotFoundError(f'邮政区域不存在: {code}')
            
        data = request.get_json()
        if not data:
            raise ValidationError('无效的请求数据')
            
        # 验证基础费用
        if 'base_fee' in data:
            try:
                base_fee = float(data['base_fee'])
                if base_fee < 0:
                    raise ValueError
                data['base_fee'] = base_fee
            except ValueError:
                raise ValidationError('基础费用必须是非负数')
                
        # 更新邮政区域
        for field in ['name', 'description', 'base_fee', 'is_active']:
            if field in data:
                setattr(zone, field, data[field])
                
        zone.updated_at = datetime.now()
        db.session.commit()
        
        logger.info(f"更新邮政区域成功: {code}")
        return jsonify({
            'message': '更新成功',
            'postal_zone': zone.to_dict()
        })
        
    except ResourceNotFoundError as e:
        logger.warning(str(e))
        return jsonify({'message': str(e)}), 404
    except ValidationError as e:
        logger.warning(f"更新邮政区域验证错误: {str(e)}")
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        logger.error(f"更新邮政区域失败: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({'message': '更新邮政区域失败'}), 500

@bp.route('/<string:code>', methods=['DELETE'])
@login_required
@admin_required
def delete_postal_zone(code):
    """删除邮政区域"""
    try:
        zone = PostalZone.query.filter_by(code=code).first()
        if not zone:
            raise ResourceNotFoundError(f'邮政区域不存在: {code}')
            
        # 检查邮政区域是否可以删除
        if zone.orders:
            raise BusinessError('邮政区域已被使用，无法删除')
            
        db.session.delete(zone)
        db.session.commit()
        
        logger.info(f"删除邮政区域成功: {code}")
        return '', 204
        
    except ResourceNotFoundError as e:
        logger.warning(str(e))
        return jsonify({'message': str(e)}), 404
    except BusinessError as e:
        logger.warning(f"删除邮政区域业务错误: {str(e)}")
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        logger.error(f"删除邮政区域失败: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({'message': '删除邮政区域失败'}), 500

@bp.route('/check', methods=['POST'])
@login_required
def check_postal_zone():
    """检查邮政编码所属区域"""
    try:
        data = request.get_json()
        if not data:
            raise ValidationError('无效的请求数据')
            
        # 验证必填字段
        if 'postal_code' not in data:
            raise ValidationError('缺少邮政编码')
            
        postal_code = data['postal_code']
        if not postal_code:
            raise ValidationError('邮政编码不能为空')
            
        # 验证邮政编码格式
        if not re.match(r'^\d{5,6}$', postal_code):
            raise ValidationError('无效的邮政编码格式')
            
        # 查找匹配的邮政区域
        zone = PostalZone.query.filter(
            PostalZone.postal_codes.contains(postal_code)
        ).first()
        
        if not zone:
            raise BusinessError('未找到匹配的邮政区域')
            
        if not zone.is_active:
            raise BusinessError('邮政区域已禁用')
            
        logger.debug(f"检查邮政编码成功: {postal_code} -> {zone.code}")
        return jsonify({
            'postal_code': postal_code,
            'postal_zone': zone.to_dict()
        })
        
    except ValidationError as e:
        logger.warning(f"检查邮政编码验证错误: {str(e)}")
        return jsonify({'message': str(e)}), 400
    except BusinessError as e:
        logger.warning(f"检查邮政编码业务错误: {str(e)}")
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        logger.error(f"检查邮政编码失败: {str(e)}", exc_info=True)
        return jsonify({'message': '检查邮政编码失败'}), 500

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

# 收件邮编相关路由
@bp.route('/receiver', methods=['GET'])
def get_receiver_postal_zones():
    """获取收件邮编列表"""
    try:
        postals = PostalZone.query.filter_by(type='receiver').order_by(PostalZone.start_code).all()
        data = [postal.to_dict() for postal in postals]
        return jsonify({
            'success': True,
            'data': data,
            'message': '获取成功'
        })
    except Exception as e:
        logger.error(f'获取收件邮编列表失败: {str(e)}')
        return jsonify({
            'success': False,
            'data': [],
            'message': '获取收件邮编列表失败'
        })

@bp.route('/receiver', methods=['POST'])
@login_required
@admin_required
def create_receiver_postal():
    """创建收件邮编"""
    try:
        data = request.get_json()
        if not data:
            raise ValidationError('无效的请求数据')

        # 验证必填字段
        required_fields = ['start_code', 'zone_id']
        for field in required_fields:
            if not data.get(field):
                raise ValidationError(f'缺少必填字段: {field}')

        # 创建收件邮编
        postal = PostalZone(
            start_code=data['start_code'],
            zone_id=data['zone_id'],
            type='receiver',
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        db.session.add(postal)
        db.session.commit()

        return jsonify({
            'message': '创建成功',
            'data': postal.to_dict()
        }), 201

    except ValidationError as e:
        logger.warning(f"创建收件邮编验证错误: {str(e)}")
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        logger.error(f"创建收件邮编失败: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({'message': '创建收件邮编失败'}), 500

@bp.route('/receiver/<int:id>', methods=['PUT'])
@login_required
@admin_required
def update_receiver_postal(id):
    """更新收件邮编"""
    try:
        postal = PostalZone.query.filter_by(id=id, type='receiver').first()
        if not postal:
            raise ResourceNotFoundError(f'收件邮编不存在: {id}')

        data = request.get_json()
        if not data:
            raise ValidationError('无效的请求数据')

        # 更新字段
        for field in ['start_code', 'zone_id']:
            if field in data:
                setattr(postal, field, data[field])

        postal.updated_at = datetime.now()
        db.session.commit()

        return jsonify({
            'message': '更新成功',
            'data': postal.to_dict()
        })

    except ResourceNotFoundError as e:
        logger.warning(str(e))
        return jsonify({'message': str(e)}), 404
    except ValidationError as e:
        logger.warning(f"更新收件邮编验证错误: {str(e)}")
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        logger.error(f"更新收件邮编失败: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({'message': '更新收件邮编失败'}), 500

@bp.route('/receiver/<int:id>', methods=['DELETE'])
@login_required
@admin_required
def delete_receiver_postal(id):
    """删除收件邮编"""
    try:
        postal = PostalZone.query.filter_by(id=id, type='receiver').first()
        if not postal:
            raise ResourceNotFoundError(f'收件邮编不存在: {id}')

        db.session.delete(postal)
        db.session.commit()

        return '', 204

    except ResourceNotFoundError as e:
        logger.warning(str(e))
        return jsonify({'message': str(e)}), 404
    except Exception as e:
        logger.error(f"删除收件邮编失败: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({'message': '删除收件邮编失败'}), 500

@bp.route('/receiver/<int:id>/details', methods=['GET'])
def get_receiver_postal_details(id):
    try:
        postal = PostalZone.query.get(id)
        if not postal or postal.type != 'receiver':
            return jsonify({
                'success': False,
                'message': '找不到该邮编记录'
            })

        if not postal.excel_content:
            return jsonify({
                'success': True,
                'data': []
            })

        try:
            # 从数据库中读取Excel内容
            df = pd.read_json(postal.excel_content)
            details = df.to_dict('records')
            return jsonify({
                'success': True,
                'data': details
            })
        except Exception as e:
            current_app.logger.error(f'解析Excel内容失败: {str(e)}')
            return jsonify({
                'success': False,
                'message': f'解析Excel内容失败: {str(e)}'
            })

    except Exception as e:
        current_app.logger.error(f'获取收件邮编详情失败: {str(e)}')
        return jsonify({
            'success': False,
            'message': f'获取详情失败: {str(e)}'
        })

# 偏远邮编相关路由
@bp.route('/remote', methods=['GET'])
def get_remote_postal_zones():
    """获取偏远邮编列表"""
    try:
        postals = PostalZone.query.filter_by(type='remote').order_by(PostalZone.start_code).all()
        data = [postal.to_dict() for postal in postals]
        return jsonify({
            'success': True,
            'data': data,
            'message': '获取成功'
        })
    except Exception as e:
        logger.error(f'获取偏远邮编列表失败: {str(e)}')
        return jsonify({
            'success': False,
            'data': [],
            'message': '获取偏远邮编列表失败'
        })

@bp.route('/remote', methods=['POST'])
@login_required
@admin_required
def create_remote_postal():
    """创建偏远邮编"""
    try:
        data = request.get_json()
        if not data:
            raise ValidationError('无效的请求数据')

        # 验证必填字段
        required_fields = ['start_code', 'zone_id']
        for field in required_fields:
            if not data.get(field):
                raise ValidationError(f'缺少必填字段: {field}')

        # 创建偏远邮编
        postal = PostalZone(
            start_code=data['start_code'],
            zone_id=data['zone_id'],
            type='remote',
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        db.session.add(postal)
        db.session.commit()

        return jsonify({
            'message': '创建成功',
            'data': postal.to_dict()
        }), 201

    except ValidationError as e:
        logger.warning(f"创建偏远邮编验证错误: {str(e)}")
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        logger.error(f"创建偏远邮编失败: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({'message': '创建偏远邮编失败'}), 500

@bp.route('/remote/<int:id>', methods=['PUT'])
@login_required
@admin_required
def update_remote_postal(id):
    """更新偏远邮编"""
    try:
        postal = PostalZone.query.filter_by(id=id, type='remote').first()
        if not postal:
            raise ResourceNotFoundError(f'偏远邮编不存在: {id}')

        data = request.get_json()
        if not data:
            raise ValidationError('无效的请求数据')

        # 更新字段
        for field in ['start_code', 'zone_id']:
            if field in data:
                setattr(postal, field, data[field])

        postal.updated_at = datetime.now()
        db.session.commit()

        return jsonify({
            'message': '更新成功',
            'data': postal.to_dict()
        })

    except ResourceNotFoundError as e:
        logger.warning(str(e))
        return jsonify({'message': str(e)}), 404
    except ValidationError as e:
        logger.warning(f"更新偏远邮编验证错误: {str(e)}")
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        logger.error(f"更新偏远邮编失败: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({'message': '更新偏远邮编失败'}), 500

@bp.route('/remote/<int:id>', methods=['DELETE'])
@login_required
@admin_required
def delete_remote_postal(id):
    """删除偏远邮编"""
    try:
        postal = PostalZone.query.filter_by(id=id, type='remote').first()
        if not postal:
            raise ResourceNotFoundError(f'偏远邮编不存在: {id}')

        db.session.delete(postal)
        db.session.commit()

        return '', 204

    except ResourceNotFoundError as e:
        logger.warning(str(e))
        return jsonify({'message': str(e)}), 404
    except Exception as e:
        logger.error(f"删除偏远邮编失败: {str(e)}", exc_info=True)
        db.session.rollback()
        return jsonify({'message': '删除偏远邮编失败'}), 500

@bp.route('/import-zone-excel', methods=['POST'])
@login_required
@admin_required
def import_zone_excel():
    """导入邮编分区Excel文件"""
    try:
        logger.info("开始处理Excel导入请求")
        
        # 检查文件是否存在
        if 'file' not in request.files:
            logger.warning("未找到上传的文件")
            return jsonify({'success': False, 'message': '请选择Excel文件'}), 400
        
        file = request.files['file']
        if not file or not file.filename:
            logger.warning("文件名为空")
            return jsonify({'success': False, 'message': '请选择文件'}), 400
            
        if not file.filename.endswith(('.xlsx', '.xls')):
            logger.warning(f"文件格式错误: {file.filename}")
            return jsonify({'success': False, 'message': '请选择正确的Excel文件格式(.xlsx或.xls)'}), 400

        # 检查并验证起始邮编
        start_code = request.form.get('start_code', '').strip()
        if not start_code or not re.match(r'^\d{5}$', start_code):
            logger.warning(f"起始邮编格式错误: {start_code}")
            return jsonify({'success': False, 'message': '起始邮编必须是5位数字'}), 400

        # 保存文件到临时目录
        temp_path = os.path.join(tempfile.gettempdir(), secure_filename(file.filename))
        file.save(temp_path)
        logger.info(f"文件已保存到临时目录: {temp_path}")

        try:
            # 读取Excel文件内容
            df = pd.read_excel(
                temp_path,
                dtype=str,  # 将所有列设置为字符串类型
                keep_default_na=False  # 防止空值被转换为NaN
            )
            
            # 立即处理所有列，确保保持原始格式
            for col in df.columns:
                # 先转为字符串并去除空格
                df[col] = df[col].apply(lambda x: str(x).strip())
                # 检查是否是邮编列
                if any(name in col for name in ['ZIP', 'zip', '邮编']):
                    # 直接使用字符串处理，保持原始格式
                    df[col] = df[col].apply(lambda x: x.zfill(5) if x.isdigit() else x)
            
            logger.info(f"成功读取Excel文件，包含 {len(df)} 行数据")
            logger.info(f"Excel列名: {df.columns.tolist()}")
            logger.info(f"数据示例:\n{df.head().to_string()}")  # 打印前几行数据用于检查
            
            # 清理数据：删除所有空列
            df = df.dropna(axis=1, how='all')
            
            # 检查并规范化列名
            column_mappings = {
                'col1': ['Destination ZIP Codes', 'ZIP', 'zip', '邮编', 'ZIP Codes', 'Destination ZIP codes'],
                'col2': ['Destination ZIP Codes.1', 'ZIP.1', 'zip.1', '邮编.1'],
                'col3': ['Destination ZIP Codes.2', 'ZIP.2', 'zip.2', '邮编.2'],
                'col4': ['Destination ZIP Codes.3', 'ZIP.3', 'zip.3', '邮编.3'],
                'col5': ['Destination ZIP Codes.4', 'ZIP.4', 'zip.4', '邮编.4']
            }
            
            # 重命名列以统一格式
            found_columns = {}
            for target_col, possible_names in column_mappings.items():
                for col_name in df.columns:
                    if col_name.strip() in possible_names:
                        found_columns[target_col] = col_name
                        break
            
            df = df.rename(columns={v: k for k, v in found_columns.items()})
            
            # 最后一次确保所有邮编列的格式正确
            for col in df.columns:
                if col.startswith('col'):
                    # 直接使用字符串处理，保持原始格式
                    df[col] = df[col].apply(lambda x: x.zfill(5) if x.isdigit() else x)
            
            logger.info(f"处理后的数据示例:\n{df.head().to_string()}")  # 再次打印检查
            
            # 将Excel内容转换为JSON字符串
            excel_content = df.to_json(orient='records', force_ascii=False)
            logger.info(f"转换后的JSON内容(前200字符): {excel_content[:200]}")
            
        except Exception as e:
            logger.error(f"读取Excel文件失败: {str(e)}")
            return jsonify({'success': False, 'message': f'读取Excel文件失败: {str(e)}'}), 400
        finally:
            # 删除临时文件
            if os.path.exists(temp_path):
                os.remove(temp_path)

        if len(df.columns) < 2:
            logger.warning("Excel文件格式错误：列数不足")
            return jsonify({'success': False, 'message': 'Excel文件必须包含至少两列：邮编范围和分区'}), 400

        # 创建或更新记录
        postal = PostalZone.query.filter_by(start_code=start_code, type='receiver').first()
        if postal:
            postal.excel_content = excel_content
            postal.file_name = secure_filename(file.filename)
        else:
            postal = PostalZone(
                start_code=start_code,
                type='receiver',
                excel_content=excel_content,
                file_name=secure_filename(file.filename)
            )
            db.session.add(postal)

        try:
            db.session.commit()
            logger.info(f"数据库事务提交成功")
            return jsonify({
                'success': True,
                'message': '导入成功',
                'data': [postal.to_dict()]
            })
        except Exception as e:
            db.session.rollback()
            logger.error(f"数据库事务提交失败: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'保存数据失败：{str(e)}'
            }), 500

    except Exception as e:
        logger.error(f"导入过程发生未预期的错误: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'导入失败：{str(e)}'
        }), 500

@bp.route('/receiver/import', methods=['POST'])
def import_receiver_postal():
    try:
        logger.info("开始处理收件邮编导入请求")
        
        # 检查文件
        file = request.files.get('file')
        if not file or not file.filename:
            logger.warning("未找到上传的文件")
            return jsonify({'success': False, 'message': '请选择Excel文件'})
            
        if not file.filename.endswith(('.xlsx', '.xls')):
            logger.warning(f"文件格式错误: {file.filename}")
            return jsonify({'success': False, 'message': '请选择正确的Excel文件格式(.xlsx或.xls)'})

        # 检查起始邮编
        start_code = request.form.get('start_code', '').strip()
        if not start_code or not re.match(r'^\d{5}$', start_code):
            logger.warning(f"起始邮编格式错误: {start_code}")
            return jsonify({'success': False, 'message': '起始邮编必须是5位数字'})

        # 保存文件到临时路径
        temp_path = os.path.join(tempfile.gettempdir(), secure_filename(file.filename))
        file.save(temp_path)
        logger.info(f"文件已保存到临时目录: {temp_path}")

        try:
            # 读取Excel文件内容
            df = pd.read_excel(temp_path)
            logger.info(f"成功读取Excel文件，包含 {len(df)} 行数据")
            logger.info(f"Excel列名: {df.columns.tolist()}")
            
            # 检查并规范化列名
            column_mappings = {
                'Destination ZIP': ['Destination ZIP', 'destination_zip', 'zip', '目的地邮编', '邮编'],
                'Zone': ['Zone', 'zone', '分区', '区域']
            }
            
            found_columns = {}
            for target_col, possible_names in column_mappings.items():
                for col_name in df.columns:
                    if col_name.strip().lower() in [name.strip().lower() for name in possible_names]:
                        found_columns[target_col] = col_name
                        break
                        
            if len(found_columns) != len(column_mappings):
                missing_cols = set(column_mappings.keys()) - set(found_columns.keys())
                logger.warning(f"Excel文件缺少必要的列: {missing_cols}")
                return jsonify({
                    'success': False,
                    'message': f'Excel文件格式错误，缺少以下列: {", ".join(missing_cols)}'
                })
                
            # 重命名列以统一格式
            df = df.rename(columns=found_columns)
            
            # 将Excel内容转换为JSON字符串
            excel_content = df.to_json(orient='records')
            logger.info("成功将Excel内容转换为JSON格式")
            
            # 创建或更新postal记录
            try:
                postal = PostalZone.query.filter_by(start_code=start_code, type='receiver').first()
                if postal:
                    logger.info(f"更新现有记录，ID: {postal.id}")
                    postal.excel_content = excel_content
                    postal.file_name = secure_filename(file.filename)
                    postal.updated_at = datetime.now()
                    logger.info("已更新excel_content和file_name")
                else:
                    logger.info("创建新记录")
                    postal = PostalZone(
                        start_code=start_code,
                        type='receiver',
                        excel_content=excel_content,
                        file_name=secure_filename(file.filename),
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )
                    db.session.add(postal)
                    logger.info("已创建新的PostalZone记录")
                
                db.session.commit()
                logger.info("成功保存到数据库")
                
                result = postal.to_dict()
                logger.info(f"返回结果: {result}")
                
                return jsonify({
                    'success': True,
                    'message': '导入成功',
                    'data': result
                })

            except Exception as e:
                db.session.rollback()
                logger.error(f"数据库操作失败: {str(e)}", exc_info=True)
                return jsonify({
                    'success': False, 
                    'message': f'保存数据失败: {str(e)}'
                })

        finally:
            # 删除临时文件
            if os.path.exists(temp_path):
                os.remove(temp_path)
                logger.info("已删除临时文件")

    except Exception as e:
        logger.error(f"导入过程发生未预期的错误: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'导入失败: {str(e)}'
        })

@bp.route('/remote/import', methods=['POST'])
def import_remote_postal():
    try:
        logger.info("开始处理偏远邮编导入请求")
        
        # 检查文件
        file = request.files.get('file')
        if not file or not file.filename:
            logger.warning("未找到上传的文件")
            return jsonify({'success': False, 'message': '请选择Excel文件'})
            
        if not file.filename.endswith(('.xlsx', '.xls')):
            logger.warning(f"文件格式错误: {file.filename}")
            return jsonify({'success': False, 'message': '请选择正确的Excel文件格式(.xlsx或.xls)'})

        # 检查起始邮编
        start_code = request.form.get('start_code', '').strip()
        if not start_code or not re.match(r'^\d{5}$', start_code):
            logger.warning(f"起始邮编格式错误: {start_code}")
            return jsonify({'success': False, 'message': '起始邮编必须是5位数字'})

        # 保存文件到临时路径
        temp_path = os.path.join(tempfile.gettempdir(), secure_filename(file.filename))
        file.save(temp_path)
        logger.info(f"文件已保存到临时目录: {temp_path}")

        try:
            # 读取Excel文件内容，确保所有数据都作为字符串读取
            df = pd.read_excel(
                temp_path,
                dtype=str,  # 将所有列设置为字符串类型
                keep_default_na=False,  # 防止空值被转换为NaN
                na_filter=False  # 禁用NA过滤，保持原始数据
            )
            
            logger.info(f"原始Excel列名: {df.columns.tolist()}")
            logger.info(f"原始数据示例:\n{df.head().to_string()}")
            
            # 清理数据：删除所有空列
            df = df.dropna(axis=1, how='all')
            
            # 删除不需要的列（Unnamed列）
            df = df.loc[:, ~df.columns.str.contains('Unnamed')]
            
            # 获取原始列名和第一行（作为第二行表头）
            original_columns = df.columns.tolist()
            second_header = df.iloc[0].to_dict()
            
            # 保存表头信息
            headers = {
                'first_row': original_columns,
                'second_row': second_header
            }
            
            # 跳过第一行（第二行表头），处理实际数据
            df = df.iloc[1:]
            
            # 处理所有列，确保邮编格式正确
            for col in original_columns:
                # 先转为字符串并去除空格
                df[col] = df[col].astype(str).apply(lambda x: x.strip())
                # 对数字进行补零处理，保持非数字值不变
                df[col] = df[col].apply(lambda x: x.zfill(5) if x.isdigit() and len(x.strip()) <= 5 else x)
                # 记录一些示例值用于调试
                sample_values = df[col].head().tolist()
                logger.info(f"列 {col} 处理后的示例值: {sample_values}")
            
            logger.info(f"处理后的列名: {original_columns}")
            logger.info(f"处理后的数据示例:\n{df.head().to_string()}")
            
            # 将DataFrame转换为字典列表，确保保持字符串格式
            records = df.to_dict('records')
            
            # 构建完整的数据结构
            complete_data = {
                'headers': headers,
                'data': records
            }
            
            # 转换为JSON字符串
            excel_content = json.dumps(complete_data, ensure_ascii=False)
            logger.info(f"JSON内容示例(前200字符): {excel_content[:200]}")
            
            # 创建或更新postal记录
            try:
                postal = PostalZone.query.filter_by(start_code=start_code, type='remote').first()
                if postal:
                    logger.info(f"更新现有记录，ID: {postal.id}")
                    postal.excel_content = excel_content
                    postal.file_name = secure_filename(file.filename)
                    postal.updated_at = datetime.now()
                else:
                    logger.info("创建新记录")
                    postal = PostalZone(
                        start_code=start_code,
                        type='remote',
                        excel_content=excel_content,
                        file_name=secure_filename(file.filename),
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )
                    db.session.add(postal)
                
                db.session.commit()
                logger.info("成功保存到数据库")
                
                result = postal.to_dict()
                logger.info(f"返回结果: {result}")
                
                return jsonify({
                    'success': True,
                    'message': '导入成功',
                    'data': result
                })

            except Exception as e:
                db.session.rollback()
                logger.error(f"数据库操作失败: {str(e)}", exc_info=True)
                return jsonify({
                    'success': False, 
                    'message': f'保存数据失败: {str(e)}'
                })

        finally:
            # 删除临时文件
            if os.path.exists(temp_path):
                os.remove(temp_path)
                logger.info("已删除临时文件")

    except Exception as e:
        logger.error(f"导入过程发生未预期的错误: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'导入失败: {str(e)}'
        })

@bp.route('/remote/<int:id>/details', methods=['GET'])
def get_remote_postal_details(id):
    """获取偏远邮编详情"""
    try:
        postal = PostalZone.query.get(id)
        if not postal or postal.type != 'remote':
            return jsonify({
                'success': False,
                'message': '找不到该邮编记录'
            })

        if not postal.excel_content:
            return jsonify({
                'success': True,
                'data': []
            })

        try:
            # 直接解析JSON字符串，避免pandas的自动类型转换
            content = json.loads(postal.excel_content)
            
            # 从保存的数据中获取表头和数据
            headers = content['headers']
            data = content['data']
            
            # 构建第一行表头
            first_header = {}
            for col in headers['first_row']:
                first_header[col] = col
            
            # 构建完整的数据列表，包含双层表头
            formatted_data = [
                first_header,  # 第一行表头
                headers['second_row'],  # 第二行表头
            ]
            formatted_data.extend(data)  # 添加实际数据
            
            logger.info(f"处理后的数据示例: {str(formatted_data[:3])}")  # 记录前三条数据用于调试
            
            return jsonify({
                'success': True,
                'data': formatted_data
            })
        except Exception as e:
            logger.error(f'解析Excel内容失败: {str(e)}')
            return jsonify({
                'success': False,
                'message': f'解析Excel内容失败: {str(e)}'
            })

    except Exception as e:
        logger.error(f'获取偏远邮编详情失败: {str(e)}')
        return jsonify({
            'success': False,
            'message': f'获取详情失败: {str(e)}'
        }) 