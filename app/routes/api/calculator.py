import logging
import math
import json
from turtle import done
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.models.product import Product
from app.models.fuel_rate import FuelRate
from app.models.postal_zone import PostalZone
from app.utils.exceptions import ValidationError, ResourceNotFoundError, BusinessError
from app.extensions import db
from datetime import datetime
from app.decorators import calculator_required

bp = Blueprint('calculator', __name__, url_prefix='/calculator')
logger = logging.getLogger(__name__)

def cm_to_inch(cm):
    """将厘米转换为英寸并向上取整"""
    return math.ceil(float(cm) / 2.54)

def kg_to_lb(kg):
    """将千克转换为磅并向上取整"""
    return math.ceil(float(kg) * 2.20462)

def find_zone_info(from_postal, to_postal):
    """查找区域信息"""
    try:
        # 获取区域数据
        postal = PostalZone.query.filter_by(start_code=from_postal).first()
        if not postal:
            raise ValidationError('起始邮编不存在，请检查后重试')
        
        zone_data = json.loads(postal.excel_content)
        zone = None
        
        # 查找区域
        for entry in zone_data:
            zip_range = entry['Destination ZIP']
            if '-' in zip_range:
                start, end = zip_range.split('-')
                if start.strip() <= to_postal <= end.strip():
                    zone = entry['Zone']
                    break
        
        if not zone:
            raise ValidationError('目的邮编不存在，请检查后重试')
        
        # 获取偏远邮编数据
        remote_postal = PostalZone.query.filter_by(type='remote').first()
        if not remote_postal:
            return {'zone': zone, 'is_remote': False}
        
        try:
            remote_data = json.loads(remote_postal.excel_content) if isinstance(remote_postal.excel_content, str) else remote_postal.excel_content
            is_remote = False
            remote_type = None
            
            logger.info(f"检查偏远邮编表中是否存在邮编: {to_postal}")
            logger.info(f"偏远邮编数据类型: {type(remote_data)}")
            
            # 获取实际的数据数组
            data_array = []
            if isinstance(remote_data, dict):
                if 'data' in remote_data:
                    try:
                        # 如果 data 是字符串，尝试解析它
                        if isinstance(remote_data['data'], str):
                            data_array = json.loads(remote_data['data'])
                        else:
                            data_array = remote_data['data']
                    except Exception as e:
                        logger.error(f"解析data字段失败: {str(e)}")
                        data_array = []
            else:
                data_array = remote_data
                
            logger.info(f"处理的数据数组长度: {len(data_array)}")
            
            # 遍历数据数组
            for row in data_array:
                if not isinstance(row, dict):
                    logger.info(f"跳过非字典类型的行: {type(row)}")
                    continue
                
                # 检查第一列 DAS
                das_value = row.get('DAS')
                logger.info(f"DAS列值: {das_value}")
                
                if das_value:
                    postal_code = str(das_value).strip().zfill(5)
                    to_check = to_postal.strip().zfill(5)
                    logger.info(f"比较邮编: {postal_code} vs {to_check}")
                    
                    if postal_code == to_check:
                        is_remote = True
                        remote_type = 'DAS'
                        logger.info(f"在DAS列找到匹配的邮编: {postal_code}")
                        break
                
                # 如果第一列没找到，检查其他列
                for col_name, value in row.items():
                    if not value or col_name == 'DAS':  # 跳过空值和已检查的DAS列
                        continue
                    
                    # 确保邮编格式统一
                    postal_code = str(value).strip().zfill(5)
                    to_check = to_postal.strip().zfill(5)
                    
                    # 检查是否匹配
                    if postal_code == to_check:
                        is_remote = True
                        # 根据列名确定类型
                        if 'DAS_EXT' in col_name:
                            remote_type = 'DAS_EXT'
                        elif 'DAS_Remote' in col_name:
                            remote_type = 'DAS_Remote'
                        elif 'DAS_Alaska' in col_name:
                            remote_type = 'DAS_Alaska'
                        elif 'DAS_Hawaii' in col_name:
                            remote_type = 'DAS_Hawaii'
                        
                        logger.info(f"在列 {col_name} 找到匹配的邮编: {postal_code}")
                        logger.info(f"偏远地区类型: {remote_type}")
                        break
                
                if is_remote:
                    break
            
            return {
                'zone': zone,
                'is_remote': is_remote,
                'remote_type': remote_type
            }
            
        except Exception as e:
            logger.error(f"处理偏远邮编数据失败: {str(e)}")
            # 如果处理偏远邮编数据失败，仍然返回区域信息，但标记为非偏远
            return {
                'zone': zone,
                'is_remote': False
            }
        
    except ValidationError as e:
        logger.error(f"查找区域信息失败: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"查找区域信息失败: {str(e)}")
        raise ValidationError('系统错误，请稍后重试')

def get_current_pss_amount(surcharge, current_date):
    """获取当前生效的PSS金额"""
    logger.debug(f"\n=== 开始计算PSS金额 ===")
    logger.debug(f"附加费类型: {surcharge.get('title', '未知')}")
    logger.debug(f"当前日期: {current_date.date()}")
    
    if not surcharge.get('pss_periods'):
        logger.debug("没有找到PSS期间配置")
        return 0.0
        
    logger.debug("PSS期间配置:")
    for period in surcharge['pss_periods']:
        logger.debug(f"- {period['start_date']} 到 {period['end_date']}: ${period['amount']}")
    
    for period in surcharge['pss_periods']:
        try:
            start_date = datetime.strptime(period['start_date'], '%Y-%m-%d').date()
            end_date = datetime.strptime(period['end_date'], '%Y-%m-%d').date()
            logger.debug(f"\n检查期间: {start_date} 到 {end_date}")
            logger.debug(f"比较: {start_date} <= {current_date.date()} <= {end_date}")
            
            if start_date <= current_date.date() <= end_date:
                amount = float(period['amount'])
                logger.debug(f"匹配成功! 使用PSS金额: ${amount}")
                return amount
        except ValueError as e:
            logger.error(f"日期格式错误: {e}")
            logger.error(f"期间数据: {period}")
            continue
            
    logger.debug("没有找到匹配的PSS期间")
    return 0.0

def get_fee_with_pss(base_fee, surcharge, current_date):
    """计算包含PSS的费用"""
    logger.debug(f"\n=== 计算费用 ===")
    logger.debug(f"附加费类型: {surcharge.get('title', '未知')}")
    logger.debug(f"基础费用: ${base_fee}")
    
    fee = float(base_fee)
    pss_amount = get_current_pss_amount(surcharge, current_date)
    
    if pss_amount > 0:
        fee += pss_amount
        logger.debug(f"计算结果: ${fee} (基础费用: ${base_fee} + PSS: ${pss_amount})")
    else:
        logger.debug(f"计算结果: ${fee} (无PSS费用)")
        
    return fee, pss_amount

def get_zone_info(from_postal, to_postal):
    """获取区域信息"""
    if not from_postal or not to_postal:
        return None
        
    # 查找邮编对应的区域信息
    logger.info(f"查询起始邮编区域: {from_postal}")
    postal_zone = PostalZone.query.filter_by(start_code=from_postal).first()
    
    if not postal_zone:
        logger.warning(f"未找到起始邮编 {from_postal} 的区域信息")
        return None
        
    # 解析Excel内容
    try:
        zone_data = json.loads(postal_zone.excel_content) if isinstance(postal_zone.excel_content, str) else postal_zone.excel_content
        logger.debug(f"区域数据: {zone_data}")
        
        # 查找目的地邮编对应的区域
        logger.info(f"查找目的地邮编区域: {to_postal}")
        for entry in zone_data:
            zip_range = entry.get('Destination ZIP', '').split('-')
            if len(zip_range) == 2:
                start_zip = zip_range[0].strip()
                end_zip = zip_range[1].strip()
                if start_zip <= to_postal <= end_zip:
                    logger.info(f"找到匹配的区域: {entry.get('Zone')}")
                    return {
                        'zone': entry.get('Zone'),
                        'is_remote': False  # 暂时默认为非偏远地区
                    }
                    
        logger.warning(f"未找到目的地邮编 {to_postal} 的区域信息")
        return None
        
    except Exception as e:
        logger.error(f"解析区域数据失败: {str(e)}")
        return None

@bp.route('/calculate', methods=['POST'])
@login_required
@calculator_required
def calculate():
    try:
        current_date = datetime.now()
        data = request.get_json()
        logger.info("收到计算请求数据:")
        logger.info(f"起始邮编: {data.get('fromPostalCode')}")
        logger.info(f"目的邮编: {data.get('toPostalCode')}")
        logger.info(f"重量(kg): {data.get('weight')}")
        logger.info(f"长度(cm): {data.get('length')}")
        logger.info(f"宽度(cm): {data.get('width')}")
        logger.info(f"高度(cm): {data.get('height')}")
            
        # 验证必填字段
        required_fields = ['fromPostalCode', 'weight', 'length', 'width', 'height', 'product_id']
        for field in required_fields:
            if not data.get(field):
                raise ValidationError(f'缺少必填字段: {field}')
                
        # 获取产品信息
        product = Product.query.get(data['product_id'])
        if not product:
            raise ValidationError('产品不存在')
            
        # 加载费率表
        zone_rates = json.loads(product.zone_rates) if isinstance(product.zone_rates, str) else product.zone_rates
        if not zone_rates:
            raise ValidationError('产品费率未设置')

        # 获取DIM值，如果为空则使用默认值250
        dim_factor = float(product.volume_weight_factor if product.volume_weight_factor is not None else 250)
        logger.info(f"使用DIM系数: {dim_factor}")

        # 先转换尺寸为英寸
        length_inch = math.ceil(float(data['length']) * 0.393701)  # cm to inch
        width_inch = math.ceil(float(data['width']) * 0.393701)   # cm to inch
        height_inch = math.ceil(float(data['height']) * 0.393701)  # cm to inch

        logger.info(f"尺寸: {length_inch}inch x {width_inch}inch x {height_inch}inch")

        # 使用英寸尺寸计算体积重量
        volume_weight_lb = math.ceil((length_inch * width_inch * height_inch) / dim_factor)
        logger.info(f"体积重量: {volume_weight_lb}lb")

        # 计算实际重量(kg转lb)
        actual_weight_lb = math.ceil(float(data['weight']) * 2.20462)
        logger.info(f"实际重量: {actual_weight_lb}lb")

        # 取较大值作为计费重量
        chargeable_weight = max(actual_weight_lb, volume_weight_lb)
        logger.info(f"计费重量: {chargeable_weight}lb")

        # 计算周长和总长度
        girth = 2 * (width_inch + height_inch)
        total_length_girth = length_inch + girth

        # 如果没有提供目的地邮编，计算所有分区的费用
        if not data.get('toPostalCode'):
            results = []
            for zone in range(2, 9):  # 计算Zone 2-8的费用
                try:
                    zone_result = calculate_for_zone(
                        zone=zone,
                        product=product,
                        zone_rates=zone_rates,
                        weight_lb=actual_weight_lb,
                        volume_weight_lb=volume_weight_lb,
                        chargeable_weight=chargeable_weight,
                        length_inch=length_inch,
                        width_inch=width_inch,
                        height_inch=height_inch,
                        girth=girth,
                        total_length_girth=total_length_girth,
                        is_remote=False,  # 没有目的地邮编时不考虑偏远地区
                        is_residential=True
                    )
                    results.append(zone_result)
                except Exception as e:
                    logger.error(f"计算Zone {zone}费用时出错: {str(e)}")
                    continue

            return jsonify({
                'success': True,
                'data': {
                    'allZones': True,
                    'results': results
                }
            })

        # 如果提供了目的地邮编，使用原有逻辑
        zone_info = find_zone_info(data['fromPostalCode'], data['toPostalCode'])
        if not zone_info:
            raise ValidationError('未找到对应的区域信息，请检查邮编是否正确')
            
        logger.info(f"区域信息: {zone_info}")
        logger.info(f"是否偏远地区: {zone_info.get('is_remote', False)}")
        logger.info(f"偏远地区类型: {zone_info.get('remote_type', '-')}")
            
        result = calculate_for_zone(
            zone=zone_info['zone'],
            product=product,
            zone_rates=zone_rates,
            weight_lb=actual_weight_lb,
            volume_weight_lb=volume_weight_lb,
            chargeable_weight=chargeable_weight,
            length_inch=length_inch,
            width_inch=width_inch,
            height_inch=height_inch,
            girth=girth,
            total_length_girth=total_length_girth,
            is_remote=zone_info.get('is_remote', False),
            is_residential=True,  # 默认为住宅地址
            remote_type=zone_info.get('remote_type')
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
    except ValidationError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        logger.error(f"计算失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '系统错误，请稍后重试'
        }), 500

def calculate_for_zone(zone, product, zone_rates, weight_lb, volume_weight_lb, chargeable_weight,
                      length_inch, width_inch, height_inch, girth, total_length_girth, 
                      is_remote=False, is_residential=True, remote_type=None):
    """为指定区域计算运费"""
    zone_number = str(zone)
    logger.info(f"\n=== 开始计算区域 {zone} 的费用 ===")
    logger.info(f"实际重量: {weight_lb}lb")
    logger.info(f"体积重量: {volume_weight_lb}lb")
    logger.info(f"计费重量: {chargeable_weight}lb")
    logger.info(f"尺寸: {length_inch}inch x {width_inch}inch x {height_inch}inch")
    logger.info(f"周长: {girth}inch")
    logger.info(f"长度+周长: {total_length_girth}inch")
    
    # 检查是否为不可发包裹
    surcharges_data = json.loads(product.surcharges) if isinstance(product.surcharges, str) else product.surcharges
    logger.info("\n检查不可发包裹条件:")

    # 查找增值服务费类别
    value_added_category = next((category for category in surcharges_data 
                               if category.get('title') == '增值服务费项目'), None)

    if value_added_category:
        logger.info(f"找到增值服务费类别: {value_added_category['title']}")
        
        # 查找不可发包裹项目
        unauthorized_item = next((item for item in value_added_category.get('items', [])
                                if item.get('name') == '5. 不可发包裹(Unauthorized)'), None)
        
        if unauthorized_item:
            logger.info(f"找到不可发包裹项目: {unauthorized_item['name']}")
            logger.info(f"不可发包裹项目内容: {json.dumps(unauthorized_item, ensure_ascii=False, indent=2)}")
            
            is_unauthorized = False
            reason = None
            base_fee = 0
            pss_fee = 0

            # 检查各种不可发条件
            for sub_item in unauthorized_item.get('items', []):
                logger.info(f"检查条件: {sub_item.get('name', '')}")
                
                if '最长边+周长＞165英寸' in sub_item.get('name', '') and total_length_girth > 165:
                    is_unauthorized = True
                    reason = f"包裹长度+周长({total_length_girth}英寸)超过165英寸"
                    base_fee = float(sub_item['fees']['2'])  # 使用Zone 2的费率
                    logger.info(f"满足不可发条件: {reason}")
                    logger.info(f"基础费用: ${base_fee}")
                    break
                elif '最长边＞108英寸' in sub_item.get('name', '') and length_inch > 108:
                    is_unauthorized = True
                    reason = f"包裹最长边({length_inch}英寸)超过108英寸"
                    base_fee = float(sub_item['fees']['2'])
                    logger.info(f"满足不可发条件: {reason}")
                    logger.info(f"基础费用: ${base_fee}")
                    break
                elif '实重＞150磅' in sub_item.get('name', '') and weight_lb > 150:
                    is_unauthorized = True
                    reason = f"包裹实际重量({weight_lb}磅)超过150磅"
                    base_fee = float(sub_item['fees']['2'])
                    logger.info(f"满足不可发条件: {reason}")
                    logger.info(f"基础费用: ${base_fee}")
                    break

            if is_unauthorized:
                # 获取PSS费用
                current_time = datetime.now()
                if unauthorized_item.get('pss_periods'):
                    for period in unauthorized_item['pss_periods']:
                        start_date = datetime.strptime(period['start_date'], '%Y-%m-%d').date()
                        end_date = datetime.strptime(period['end_date'], '%Y-%m-%d').date()
                        if start_date <= current_time.date() <= end_date:
                            pss_fee = float(period['amount'])
                            logger.info(f"不可发包裹PSS费用: ${pss_fee}")
                            break

                total_fee = base_fee + pss_fee
                logger.info(f"不可发包裹基础费用: ${base_fee}")
                logger.info(f"不可发包裹总费用: ${total_fee}")

                return {
                    'zone': zone,
                    'isUnauthorized': True,
                    'reason': reason,
                    'packageInfo': {
                        'weight': {
                            'actualWeight': f"{weight_lb} 磅",
                            'volumeWeight': f"{volume_weight_lb} 磅",
                            'chargeableWeight': f"{chargeable_weight} 磅"
                        },
                        'dimensions': {
                            'length': f"{length_inch} 英寸",
                            'width': f"{width_inch} 英寸",
                            'height': f"{height_inch} 英寸",
                            'girth': f"{girth} 英寸",
                            'totalLengthGirth': f"{total_length_girth} 英寸"
                        }
                    },
                    'fee': total_fee,
                    'details': {
                        'base_fee': base_fee,
                        'pss_fee': pss_fee
                    }
                }
            else:
                logger.info("包裹不满足任何不可发条件")
        else:
            logger.info("未找到不可发包裹项目")
    else:
        logger.info("未找到增值服务费类别")

    # 如果不是不可发包裹，继续原有的计算逻辑
    # 特殊处理90磅的情况
    base_rate = 0  # 初始化base_rate
    if chargeable_weight == 90:
        # 按重量排序费率表
        sorted_rates = sorted(zone_rates, key=lambda x: float(x.get('weight', 0)))
        logger.info("\n费率表:")
        
        exact_match = next((rate for rate in sorted_rates if float(rate.get('weight', 0)) == 90), None)
        if exact_match and zone_number in exact_match:
            base_rate = float(exact_match[zone_number])
            logger.info(f"使用90磅的特殊费率: ${base_rate}")
        else:
            # 找到适用的费率
            target_rate = None
            exact_match = next((rate for rate in sorted_rates 
                          if float(rate.get('weight', 0)) == chargeable_weight), None)
            if exact_match and zone_number in exact_match:
                target_rate = exact_match
                logger.info(f"找到精确匹配的费率")
            else:
                next_rate = next((rate for rate in sorted_rates 
                            if float(rate.get('weight', 0)) >= chargeable_weight), None)
                if next_rate and zone_number in next_rate:
                    target_rate = next_rate
                    logger.info(f"使用下一档位的费率")
                elif sorted_rates and zone_number in sorted_rates[-1]:
                    target_rate = sorted_rates[-1]
                    logger.info(f"使用最高档位的费率")
            
            if not target_rate or zone_number not in target_rate:
                raise ValidationError(f'区域{zone}的费率未设置')
            
            base_rate = float(target_rate[zone_number])
            logger.info(f"基础运费: ${base_rate}")
    else:
        # 非90磅的普通处理
        sorted_rates = sorted(zone_rates, key=lambda x: float(x.get('weight', 0)))
        target_rate = None
        exact_match = next((rate for rate in sorted_rates 
                      if float(rate.get('weight', 0)) == chargeable_weight), None)
        if exact_match and zone_number in exact_match:
            target_rate = exact_match
            logger.info(f"找到精确匹配的费率")
        else:
            next_rate = next((rate for rate in sorted_rates 
                        if float(rate.get('weight', 0)) >= chargeable_weight), None)
            if next_rate and zone_number in next_rate:
                target_rate = next_rate
                logger.info(f"使用下一档位的费率")
            elif sorted_rates and zone_number in sorted_rates[-1]:
                target_rate = sorted_rates[-1]
                logger.info(f"使用最高档位的费率")
        
        if not target_rate or zone_number not in target_rate:
            raise ValidationError(f'区域{zone}的费率未设置')
        
        base_rate = float(target_rate[zone_number])
        logger.info(f"基础运费: ${base_rate}")
    
    # 初始化费用变量
    surcharges = []
    total_surcharges = 0
    oversize_fee = 0
    oversize_base_fee = 0
    oversize_pss_amount = 0
    handling_fee = 0
    residential_fee = 0
    base_fee = base_rate  # 使用计算好的base_rate
    pss_amount = 0
    service_type = None
    
    # 计算附加费
    surcharges_data = json.loads(product.surcharges) if isinstance(product.surcharges, str) else product.surcharges
    logger.info("\n=== 附加费计算 ===")
    
    # 计算额外处理费
    logger.info("\n计算额外处理费:")
    handling_fees = []  # 存储所有符合条件的额外处理费
    handling_category = next((cat for cat in surcharges_data if cat['title'] == '1. 额外处理费(Additional Handling Surcharge)'), None)
    if handling_category:
        current_time = datetime.now()
        pss_amount = 0
        
        # 获取当前生效的PSS金额
        if handling_category.get('pss_periods'):
            for period in handling_category['pss_periods']:
                start_date = datetime.strptime(period['start_date'], '%Y-%m-%d').date()
                end_date = datetime.strptime(period['end_date'], '%Y-%m-%d').date()
                if start_date <= current_time.date() <= end_date:
                    pss_amount = float(period['amount'])
                    logger.info(f"额外处理费PSS费用: ${pss_amount}")
                    break
        
        # 检查所有额外处理费条件
        for item in handling_category.get('items', []):
            fee = 0
            reason = None
            
            # 检查重量条件
            if 'weight: 50磅＜实际重量＜150磅' in item['name'] and 50 < weight_lb < 150:
                fee = float(item['fees'][zone_number])
                reason = '重量处理费'
                logger.info(f"满足额外处理费A条件: 重量{weight_lb}磅在50-150磅之间")
            
            # 检查最长边条件
            elif '48英寸＜最长边 ≤96英寸' in item['name'] and 48 < length_inch <= 96:
                fee = float(item['fees'][zone_number])
                reason = '最长边处理费'
                logger.info(f"满足额外处理费B条件: 最长边{length_inch}英寸在48-96英寸之间")
            
            # 检查长度+周长条件
            elif '105英寸＜长+周长[2*(宽+高)]≤130英寸' in item['name'] and 105 < total_length_girth <= 130:
                fee = float(item['fees'][zone_number])
                reason = '长度+周长处理费'
                logger.info(f"满足额外处理费C条件: 长度+周长{total_length_girth}英寸在105-130英寸之间")
            
            # 检查第二长边条件
            elif '第二长边＞30英寸' in item['name'] and width_inch > 30:
                fee = float(item['fees'][zone_number])
                reason = '第二长边处理费'
                logger.info(f"满足额外处理费D条件: 第二长边{width_inch}英寸大于30英寸")
            
            # 如果满足任何条件，添加到列表中
            if fee > 0:
                total_fee = fee + pss_amount
                handling_fees.append({
                    'fee': total_fee,
                    'base_fee': fee,
                    'pss_amount': pss_amount,
                    'reason': reason
                })
                logger.info(f"{reason} - 基础费用: ${fee}, PSS费用: ${pss_amount}, 总费用: ${total_fee}")
        
        # 选择费用最高的一个
        if handling_fees:
            max_handling_fee = max(handling_fees, key=lambda x: x['fee'])
            handling_fee = max_handling_fee['fee']
            handling_base_fee = max_handling_fee['base_fee']
            handling_pss_amount = max_handling_fee['pss_amount']
            logger.info(f"选择最高的额外处理费: {max_handling_fee['reason']}, 总费用: ${handling_fee}")
        else:
            handling_fee = 0
            handling_base_fee = 0
            handling_pss_amount = 0
            logger.info("没有满足条件的额外处理费")
    
    # 计算超尺寸费用
    if total_length_girth > 130 and total_length_girth <= 165 or \
       (length_inch > 96 and length_inch <= 108):
        logger.info("\n计算超尺寸费用:")
        # 如果满足超大超尺寸条件且计费重量不足90磅，按90磅计算
        if chargeable_weight < 90:
            logger.info(f"满足超大超尺寸条件且计费重量({chargeable_weight}磅)不足90磅，调整为90磅")
            chargeable_weight = 90
        
        # 遍历所有类别查找超大超尺寸费用
        for category in surcharges_data:
            logger.info(f"检查类别: {category['title']}")
            if 'items' in category:
                logger.info(f"可用的项目: {[item['name'] for item in category['items']]}")
                # 根据是否为住宅地址选择对应的类别
                if ('超大超尺寸费(Oversize-住宅地址)' in category['title'] and is_residential) or \
                   ('超大超尺寸费(Oversize-商业地址)' in category['title'] and not is_residential):
                    # 检查是否满足任一条件
                    oversize_item = None
                    if total_length_girth > 130 and total_length_girth <= 165:
                        oversize_item = next((item for item in category['items'] 
                                           if '130英寸＜长+[2*(宽+高)]≤165英寸' in item['name']), None)
                        if oversize_item:
                            logger.info(f"找到超大超尺寸项目(条件a): {oversize_item['name']}")
                    
                    if not oversize_item and length_inch > 96 and length_inch <= 108:
                        oversize_item = next((item for item in category['items']
                                           if '96英寸＜最长边≤108英寸' in item['name']), None)
                        if oversize_item:
                            logger.info(f"找到超大超尺寸项目(条件b): {oversize_item['name']}")
                    
                    if oversize_item:
                        logger.info(f"费用数据: {oversize_item['fees']}")
                        oversize_base_fee = float(oversize_item['fees'][zone_number])
                        logger.info(f"超尺寸基础费用: ${oversize_base_fee}")
                        
                        # 获取PSS费用
                        current_time = datetime.now()
                        oversize_pss_amount = 0
                        if category.get('pss_periods'):
                            logger.info("查找PSS费用...")
                            logger.info(f"PSS周期: {category['pss_periods']}")
                            for pss_period in category['pss_periods']:
                                start_date = datetime.strptime(pss_period['start_date'], '%Y-%m-%d')
                                end_date = datetime.strptime(pss_period['end_date'], '%Y-%m-%d')
                                if start_date.date() <= current_time.date() <= end_date.date():
                                    oversize_pss_amount = float(pss_period['amount'])
                                    logger.info(f"超尺寸PSS费用: ${oversize_pss_amount}")
                                    break

                        oversize_fee = oversize_base_fee + oversize_pss_amount
                        logger.info(f"超尺寸总费用: ${oversize_fee}")
                        break
            
        if oversize_fee == 0:
            logger.info("未找到超大超尺寸项目")
    
    # 计算住宅地址附加费
    logger.info("\n计算住宅地址附加费:")
    residential_surcharge = next((s for s in surcharges_data 
                                if s.get('title', '').startswith('4. 住宅地址附加费')), None)
    if residential_surcharge:
        # 获取基础费用
        if weight_lb <= 70:
            base_fee = float(next(item["fees"]["2"] for item in residential_surcharge["items"] 
                               if item["name"] == "FedEx Home Delivery"))
            service_type = "Home Delivery"
            logger.info(f"使用Home Delivery服务 (重量 <= 70lb)")
        else:
            base_fee = float(next(item["fees"]["2"] for item in residential_surcharge["items"]
                               if item["name"] == "FedEx Commercial Ground"))
            service_type = "Commercial Ground"
            logger.info(f"使用Commercial Ground服务 (重量 > 70lb)")
        
        logger.info(f"住宅地址基础费用: ${base_fee}")
        
        # 获取PSS费用
        pss_amount = 0
        current_time = datetime.now()
        for period in residential_surcharge.get("pss_periods", []):
            start_date = datetime.strptime(period["start_date"], "%Y-%m-%d").date()
            end_date = datetime.strptime(period["end_date"], "%Y-%m-%d").date()
            if start_date <= current_time.date() <= end_date:
                pss_amount = float(period["amount"])
                logger.info(f"住宅地址PSS费用: ${pss_amount}")
                break

        total_residential_fee = base_fee + pss_amount
        residential_fee = total_residential_fee
        logger.info(f"住宅地址总费用: ${residential_fee}")
    
    # 计算偏远地区附加费
    logger.info("\n计算偏远地区附加费:")
    remote_fee = 0
    remote_base_fee = 0
    remote_service_type = None

    if is_remote:
        logger.info(f"检测到偏远地区，类型: {remote_type}")
        remote_surcharge = next((s for s in surcharges_data if s.get('title', '').startswith('5. 偏远地区附加费')), None)
        
        if remote_surcharge:
            logger.info(f"找到偏远地区附加费类别: {remote_surcharge['title']}")
            logger.info(f"可用的项目: {[item['name'] for item in remote_surcharge.get('items', [])]}")
            
            # 根据remote_type和是否住宅选择对应的费率项
            remote_item = None
            if is_residential:
                if remote_type == 'DAS':
                    remote_item = next((item for item in remote_surcharge['items'] 
                                    if 'Residential (FedEx Home Delivery)' in item['name']), None)
                    remote_service_type = "Residential Home Delivery"
                elif remote_type == 'DAS_EXT':
                    remote_item = next((item for item in remote_surcharge['items']
                                    if 'Extended Residential (FedEx Home Delivery)' in item['name']), None)
                    remote_service_type = "Extended Residential Home Delivery"
                elif remote_type == 'DAS_Remote':
                    remote_item = next((item for item in remote_surcharge['items']
                                    if '远端地带-DAS Remote Resi (FedEx Home Delivery)' in item['name']), None)
                    remote_service_type = "Remote Residential Home Delivery"
            else:
                if remote_type == 'DAS':
                    remote_item = next((item for item in remote_surcharge['items'] 
                                    if 'Commercial(FedEx Ground)' in item['name']), None)
                    remote_service_type = "Commercial"
                elif remote_type == 'DAS_EXT':
                    remote_item = next((item for item in remote_surcharge['items']
                                    if 'Extended Commercial(FedEx Ground)' in item['name']), None)
                    remote_service_type = "Extended Commercial"
                elif remote_type == 'DAS_Remote':
                    remote_item = next((item for item in remote_surcharge['items']
                                    if '远端地带-DAS Remote Comm(FedEx Ground)' in item['name']), None)
                    remote_service_type = "Remote Commercial"
                elif remote_type == 'DAS_Alaska':
                    remote_item = next((item for item in remote_surcharge['items']
                                    if 'DAS Alaska Comm' in item['name']), None)
                    remote_service_type = "Alaska Commercial"
                elif remote_type == 'DAS_Hawaii':
                    remote_item = next((item for item in remote_surcharge['items']
                                    if 'DAS Hawaii Comm' in item['name']), None)
                    remote_service_type = "Hawaii Commercial"

            if remote_item:
                logger.info(f"找到匹配的偏远地区费率项: {remote_item['name']}")
                remote_base_fee = float(remote_item['fees']['2'])  # 偏远地区费用统一使用Zone2的费率
                remote_fee = remote_base_fee  # 偏远地区附加费没有PSS费用
                logger.info(f"偏远地区基础费用: ${remote_base_fee}")
                logger.info(f"偏远地区总费用: ${remote_fee}")
            else:
                logger.info(f"未找到对应的偏远地区费率项，尝试查找的服务类型: {remote_service_type}")
                logger.info(f"可用的费率项: {[item['name'] for item in remote_surcharge.get('items', [])]}")
        else:
            logger.info("未找到偏远地区附加费类别")
    else:
        logger.info("不是偏远地区，不计算偏远地区附加费")

    # 计算燃油费
    current_fuel_rate = FuelRate.query.filter_by(is_active=True).first()
    
    # 比较额外处理费和超大超尺寸费，只收取较大值
    if handling_fee > 0 and oversize_fee > 0:
        logger.info("\n比较额外处理费和超大超尺寸费:")
        logger.info(f"额外处理费: ${handling_fee}")
        logger.info(f"超大超尺寸费: ${oversize_fee}")
        if handling_fee > oversize_fee:
            logger.info("选择额外处理费（金额较大）")
            oversize_fee = 0
            oversize_base_fee = 0
            oversize_pss_amount = 0
        else:
            logger.info("选择超大超尺寸费（金额较大）")
            handling_fee = 0
            handling_base_fee = 0
            handling_pss_amount = 0
    
    # 计算总附加费（包含偏远地区附加费）
    total_surcharges = oversize_fee + residential_fee + handling_fee + remote_fee
    logger.info(f"\n计算燃油费:")
    logger.info(f"总附加费: ${total_surcharges}")
    logger.info(f"燃油费计算基数: ${base_rate + total_surcharges}")
    logger.info(f"燃油费率: {current_fuel_rate.rate}%")
    
    fuel_surcharge = round((base_rate + total_surcharges) * current_fuel_rate.rate / 100, 2) if current_fuel_rate else 0
    logger.info(f"燃油费: ${fuel_surcharge}")
    
    total_amount = round(base_rate + total_surcharges + fuel_surcharge, 2)
    logger.info(f"\n总费用: ${total_amount}")

    return {
        'zone': zone,
        'isRemote': is_remote,
        'baseRate': {
            'amount': round(base_rate, 2)
        },
        'packageInfo': {
            'weight': {
                'actualWeight': f"{weight_lb} 磅",
                'volumeWeight': f"{volume_weight_lb} 磅",
                'chargeableWeight': f"{chargeable_weight} 磅"
            },
            'dimensions': {
                'length': f"{length_inch} 英寸",
                'width': f"{width_inch} 英寸",
                'height': f"{height_inch} 英寸",
                'girth': f"{girth} 英寸",
                'totalLengthGirth': f"{total_length_girth} 英寸"
            }
        },
        'surchargeDetails': {
            'handlingFee': {
                'amount': round(handling_fee, 2),
                'details': {
                    'baseFee': round(handling_base_fee, 2),
                    'pssFee': round(handling_pss_amount, 2),
                    'reason': max_handling_fee['reason'] if handling_fees else '额外处理费'
                }
            },
            'oversizeFeeCommercial': {
                'amount': round(oversize_fee if not is_residential else 0, 2),
                'details': {
                    'baseFee': round(oversize_base_fee if not is_residential else 0, 2),
                    'pssFee': round(oversize_pss_amount if not is_residential else 0, 2),
                    'reason': '超大超尺寸费(商业)'
                }
            },
            'oversizeFeeResidential': {
                'amount': round(oversize_fee if is_residential else 0, 2),
                'details': {
                    'baseFee': round(oversize_base_fee if is_residential else 0, 2),
                    'pssFee': round(oversize_pss_amount if is_residential else 0, 2),
                    'reason': '超大超尺寸费(住宅)'
                }
            },
            'residentialFee': {
                'amount': round(residential_fee, 2),
                'details': {
                    'baseFee': round(base_fee, 2),
                    'pssFee': round(pss_amount, 2),
                    'reason': '住宅地址附加费'
                }
            },
            'remoteFee': {
                'amount': round(remote_fee, 2),
                'details': {
                    'baseFee': round(remote_base_fee, 2),
                    'pssFee': 0,
                    'reason': '偏远地区附加费',
                    'type': remote_type if is_remote else None
                }
            }
        },
        'actualWeight': weight_lb,
        'volumeWeight': volume_weight_lb,
        'chargeableWeight': chargeable_weight,
        'fuelSurcharge': {
            'amount': round(fuel_surcharge, 2),
            'rate': f"{current_fuel_rate.rate}%" if current_fuel_rate else "0%",
            'basis': round(base_rate + total_surcharges, 2)
        },
        'totalAmount': total_amount
    } 