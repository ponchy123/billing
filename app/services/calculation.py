from app import db
from app.models import Product, CalculationHistory, StartPostalCode, ReceiverPostalCode, RemotePostalCode
from app.utils.exceptions import ValidationError
from datetime import datetime
import json

def get_calculation_history(user_id=None, limit=10):
    """
    获取计算历史记录
    
    参数:
        user_id: 用户ID，如果不提供则获取所有历史
        limit: 返回记录数量限制
    返回:
        list: 计算历史记录列表
    """
    query = CalculationHistory.query
    
    if user_id:
        query = query.filter_by(user_id=user_id)
        
    return query.order_by(CalculationHistory.created_at.desc())\
        .limit(limit)\
        .all()

class CalculationService:
    """计算服务类"""
    
    def __init__(self, product):
        """初始化计算服务"""
        try:
            print("\n=== 初始化计算服务 ===")
            print(f"产品ID: {product.id}")
            print(f"产品名称: {product.name}")
            
            # 解析费率表
            if isinstance(product.zone_rates, str):
                self.zone_rates = json.loads(product.zone_rates)
            else:
                self.zone_rates = product.zone_rates
                
            print("\n费率表数据:")
            print(json.dumps(self.zone_rates, indent=2, ensure_ascii=False))
            
            # 解析附加费
            if isinstance(product.surcharges, str):
                self.surcharges = json.loads(product.surcharges)
            else:
                self.surcharges = product.surcharges
                
            print("\n附加费数据:")
            print(json.dumps(self.surcharges, indent=2, ensure_ascii=False))
            
        except json.JSONDecodeError as e:
            print(f"解析费率表JSON时出错: {str(e)}")
            self.zone_rates = []
            self.surcharges = []
        except Exception as e:
            print(f"初始化计算服务时出错: {str(e)}")
            print(f"错误详情: {e.__class__.__name__}")
            import traceback
            print(traceback.format_exc())
            self.zone_rates = []
            self.surcharges = []

    @classmethod
    def calculate_single(cls, product_id, length, width, height, weight, start_postal_code, receiver_postal_code, is_residential=False):
        """
        单个运费计算
        """
        try:
            # 验证产品
            product = Product.query.get(product_id)
            if not product:
                raise ValidationError('产品不存在')
            if product.status != 'active':
                raise ValidationError('产品未启用')
            
            print(f"\n=== 开始计算运费 ===")
            print(f"产品: {product.name}")
            print(f"产品费率表: {product.zone_rates}")
            print(f"尺寸: {length}x{width}x{height}cm")
            print(f"重量: {weight}kg")
            print(f"起始邮编: {start_postal_code}")
            print(f"目的邮编: {receiver_postal_code}")
            print(f"是否住宅地址: {is_residential}")
            
            # 创建计算服务实例
            calculation_service = cls(product)
            
            # 查找起始邮编
            start_postal = StartPostalCode.query.filter_by(postal_code=start_postal_code).first()
            if not start_postal:
                raise ValidationError('无效的起始邮编')
            
            # 查找收件邮编区域
            receiver_postal = ReceiverPostalCode.query.filter(
                ReceiverPostalCode.start_postal_id == start_postal.id,
                ReceiverPostalCode.start_range <= receiver_postal_code,
                ReceiverPostalCode.end_range >= receiver_postal_code
            ).first()
            if not receiver_postal:
                raise ValidationError('无效的收件邮编')
            
            print(f"区域: Zone {receiver_postal.zone}")
            
            # 检查是否是偏远地区
            is_remote = RemotePostalCode.query.filter_by(postal_code=receiver_postal_code).first() is not None
            
            # 计算体积重
            volume_weight = (length * width * height) / product.volume_weight_factor
            
            # 取较大值作为计费重量
            chargeable_weight = max(weight, volume_weight)
            
            try:
                # 转换单位
                weight_lb = chargeable_weight * 2.20462  # 千克转磅
                length_in = length * 0.393701  # 厘米转英寸
                width_in = width * 0.393701
                height_in = height * 0.393701

                print(f"\n=== 包裹信息 ===")
                print(f"实际重量: {weight_lb}lb")
                print(f"体积重量: {volume_weight * 2.20462}lb")
                print(f"计费重量: {weight_lb}lb")
                print(f"尺寸(英寸): {length_in}x{width_in}x{height_in}")

                # 计算长度+周长
                girth = 2 * (width_in + height_in)
                total_length = length_in + girth
                print(f"长度+周长: {total_length}inch")

                # 如果是超大超尺寸包裹，调整计费重量
                if total_length > 130 and total_length <= 165:
                    print(f"\n=== 调整计费重量 ===")
                    print(f"原始重量: {weight_lb}lb")
                    print(f"长度+周长: {total_length}inch > 130inch")
                    weight_lb = 90
                    print(f"调整后重量: {weight_lb}lb")
                
                # 计算基础运费
                print(f"\n=== 计算基础运费 ===")
                print(f"使用重量: {weight_lb}lb")
                print(f"区域: Zone {receiver_postal.zone}")
                base_fee = calculation_service._calculate_base_fee(receiver_postal.zone, weight_lb)
                print(f"基础运费: ${base_fee}")
                
                # 计算附加费
                surcharges, total_surcharges = calculation_service._calculate_surcharges(receiver_postal.zone, weight_lb, length_in, width_in, height_in, is_residential, is_remote)
                print(f"\n附加费明细:")
                for surcharge in surcharges:
                    print(f"- {surcharge['name']}: ${surcharge['total_fee']}")
                print(f"总附加费: ${total_surcharges}")

                # 计算燃油附加费
                fuel_surcharge = calculation_service._calculate_fuel_surcharge(base_fee + total_surcharges)
                print(f"\n燃油附加费: ${fuel_surcharge}")

                result = {
                    'base_fee': base_fee,  # 确保使用正确计算的基础运费
                    'surcharges': surcharges,
                    'total_surcharges': total_surcharges,
                    'fuel_surcharge': fuel_surcharge,
                    'total': base_fee + total_surcharges + fuel_surcharge
                }

                return result

            except Exception as e:
                print(f"计算过程中出错: {str(e)}")
                raise

        except Exception as e:
            print(f"计算过程中出错: {str(e)}")
            raise

    @classmethod
    def calculate_batch(cls, calculations):
        """
        批量计算运费
        
        参数:
            calculations: 计算请求列表，每个元素包含单个计算所需的所有参数
        返回:
            list: 计算结果列表
        """
        results = []
        for calc in calculations:
            try:
                result = cls.calculate_single(**calc)
                results.append({
                    'success': True,
                    'data': result,
                    'error': None
                })
            except ValidationError as e:
                results.append({
                    'success': False,
                    'data': None,
                    'error': str(e)
                })
            except Exception as e:
                results.append({
                    'success': False,
                    'data': None,
                    'error': '计算失败'
                })
        return results
    
    def _calculate_base_fee(self, zone, weight):
        """计算基础运费"""
        print(f"\n=== 计算基础运费详情 ===")
        print(f"区域: Zone {zone}")
        print(f"计费重量: {weight}lb")
        
        try:
            # 使用zone_rates
            zone_rates = self.zone_rates
            zone_key = f'Zone{zone}'
            
            print(f"\n查找区域 {zone_key} 的费率...")
            print(f"费率表数据: {json.dumps(zone_rates, indent=2, ensure_ascii=False)}")
            
            # 验证费率表数据
            if not zone_rates:
                raise ValueError("费率表为空")
            
            # 按重量排序
            sorted_rates = sorted(zone_rates, key=lambda x: float(x['weight']))
            
            # 验证区域是否存在
            if not any(zone_key in rate for rate in sorted_rates):
                raise ValueError(f"费率表中不存在区域 {zone_key}")
            
            # 打印排序后的费率表
            print("\n费率表(按重量排序):")
            for rate in sorted_rates:
                if 85 <= float(rate['weight']) <= 95:  # 只打印85-95磅范围的费率
                    print(f"- 重量: {rate['weight']}lb, {zone_key}费率: ${rate.get(zone_key, 'N/A')}")
            
            # 特别处理90磅的情况
            if abs(weight - 90) < 0.01:
                print("\n处理90磅的特殊情况...")
                # 先尝试找到精确的90磅费率
                exact_match = next((rate for rate in sorted_rates if abs(float(rate['weight']) - 90) < 0.01), None)
                if exact_match:
                    if zone_key not in exact_match:
                        print(f"错误: 在90磅费率中未找到 {zone_key} 的费率")
                        print(f"可用的区域: {list(exact_match.keys())}")
                        raise ValueError(f"90磅费率中未找到 {zone_key} 的费率")
                    base_fee = float(exact_match[zone_key])
                    print(f"找到90磅的精确费率: ${base_fee}")
                    return base_fee
                
                print("未找到90磅的精确费率，尝试查找最接近的费率...")
                # 如果没有找到精确匹配，找到大于等于90磅的最小费率
                next_rate = next((rate for rate in sorted_rates if float(rate['weight']) >= 90), None)
                if next_rate:
                    if zone_key not in next_rate:
                        print(f"错误: 在费率中未找到 {zone_key} 的费率")
                        print(f"可用的区域: {list(next_rate.keys())}")
                        raise ValueError(f"费率中未找到 {zone_key} 的费率")
                    base_fee = float(next_rate[zone_key])
                    print(f"使用大于等于90磅的最小费率 - 重量: {next_rate['weight']}lb, 费率: ${base_fee}")
                    return base_fee
                
                print("未找到大于等于90磅的费率，使用最大重量的费率...")
                # 如果没有找到大于等于90磅的费率，使用最大重量的费率
                max_rate = sorted_rates[-1]
                if zone_key not in max_rate:
                    print(f"错误: 在最大重量费率中未找到 {zone_key} 的费率")
                    print(f"可用的区域: {list(max_rate.keys())}")
                    raise ValueError(f"最大重量费率中未找到 {zone_key} 的费率")
                base_fee = float(max_rate[zone_key])
                print(f"使用最大重量级别的费率 - 重量: {max_rate['weight']}lb, 费率: ${base_fee}")
                return base_fee
            
            # 处理其他重量的情况
            print("\n处理其他重量的情况...")
            
            # 验证重量范围
            min_weight = float(sorted_rates[0]['weight'])
            max_weight = float(sorted_rates[-1]['weight'])
            if weight < min_weight:
                print(f"警告: 重量 {weight}lb 小于费率表最小重量 {min_weight}lb，使用最小重量的费率")
                base_fee = float(sorted_rates[0][zone_key])
                return base_fee
            if weight > max_weight:
                print(f"警告: 重量 {weight}lb 大于费率表最大重量 {max_weight}lb，使用最大重量的费率")
                base_fee = float(sorted_rates[-1][zone_key])
                return base_fee
            
            # 查找精确匹配或最接近的费率
            exact_match = next((rate for rate in sorted_rates if abs(float(rate['weight']) - weight) < 0.01), None)
            if exact_match:
                base_fee = float(exact_match[zone_key])
                print(f"找到精确匹配的费率 - 重量: {exact_match['weight']}lb, 费率: ${base_fee}")
                return base_fee
            
            # 找到最接近的两个重量进行插值计算
            lower_rate = next((rate for rate in reversed(sorted_rates) if float(rate['weight']) <= weight), None)
            upper_rate = next((rate for rate in sorted_rates if float(rate['weight']) > weight), None)
            
            if lower_rate and upper_rate:
                # 使用线性插值计算费率
                weight_diff = float(upper_rate['weight']) - float(lower_rate['weight'])
                fee_diff = float(upper_rate[zone_key]) - float(lower_rate[zone_key])
                weight_ratio = (weight - float(lower_rate['weight'])) / weight_diff
                base_fee = float(lower_rate[zone_key]) + (fee_diff * weight_ratio)
                print(f"使用线性插值计算费率:")
                print(f"- 下限重量: {lower_rate['weight']}lb, 费率: ${lower_rate[zone_key]}")
                print(f"- 上限重量: {upper_rate['weight']}lb, 费率: ${upper_rate[zone_key]}")
                print(f"- 计算得到的费率: ${base_fee:.2f}")
                return round(base_fee, 2)
            
            # 如果无法进行插值，使用最接近的费率
            closest_rate = min(sorted_rates, key=lambda x: abs(float(x['weight']) - weight))
            base_fee = float(closest_rate[zone_key])
            print(f"使用最接近的费率 - 重量: {closest_rate['weight']}lb, 费率: ${base_fee}")
            return base_fee
            
        except Exception as e:
            print(f"计算基础运费时出错: {str(e)}")
            print(f"错误详情: {e.__class__.__name__}")
            import traceback
            print(traceback.format_exc())
            raise
    
    def _calculate_handling_fee(self, zone, weight, length, width, height):
        """计算额外处理费"""
        print(f"计算额外处理费 - Zone: {zone}, Weight: {weight}, Dimensions: {length}x{width}x{height}")
        handling_rates = self.surcharges[0].get('items', [])  # 第一个元素是额外处理费
        
        # 重量处理费
        if 50 < weight < 150:
            for item in handling_rates:
                if '重量' in item['name']:
                    base_fee = float(item['fees'].get(str(zone), 0))
                    print(f"重量处理基础费: ${base_fee}")
                    return base_fee
            
        return 0
        
    def _calculate_width_handling_fee(self, zone, width):
        """计算第二长边处理费"""
        print(f"计算第二长边处理费 - Zone: {zone}, Width: {width}")
        handling_rates = self.surcharges[0].get('items', [])  # 第一个元素是额外处理费
        
        # 第二长边处理费
        if width > 30:
            base_fee = float(handling_rates[3]['fees'].get(str(zone), 0))  # 第四个item是第二长边处理费
            print(f"第二长边处理基础费: ${base_fee}")
            return base_fee
            
        return 0
    
    def _calculate_oversize_fee(self, zone, weight, length, width, height):
        """计算超大超尺寸费"""
        print(f"计算超大超尺寸费 - Zone: {zone}, Weight: {weight}, Dimensions: {length}x{width}x{height}")
        oversize_rates = self.surcharges[1].get('items', [])  # 第二个元素是超大超尺寸费
        
        # 计算长度+周长
        girth = 2 * (width + height)
        total_length = length + girth
        print(f"总长度(长度+周长): {total_length}")
        
        if total_length > 130 and total_length <= 165 and weight < 150:
            for item in oversize_rates:
                if '实际重量＜150磅' in item['description']:
                    base_fee = float(item['fees'].get(str(zone), 0))
                    print(f"超大超尺寸基础费: ${base_fee}")
                    return base_fee
            
        return 0
    
    def _calculate_residential_fee(self, weight):
        """计算住宅地址附加费"""
        print(f"计算住宅地址附加费 - Weight: {weight}")
        residential_rates = self.surcharges[3].get('items', [])  # 第四个元素是住宅地址附加费
        
        # 根据重量选择服务类型
        service_type = 'Home' if weight <= 70 else 'Ground'
        print(f"选择服务类型: {service_type}")
        
        for rate in residential_rates:
            if service_type in rate['name']:
                base_fee = float(rate['fees'].get('all', 0))
                print(f"住宅地址基础费: ${base_fee}")
                return base_fee
                
        return 0
    
    def _calculate_remote_area_fee(self, is_remote):
        """计算偏远地区费"""
        return 30 if is_remote else 0

    @classmethod
    def save_calculation_history(cls, user_id, calculation_data, result):
        """
        保存计算历史
        
        参数:
            user_id: 用户ID
            calculation_data: 计算请求数据
            result: 计算结果
        """
        history = CalculationHistory(
            user_id=user_id,
            product_id=calculation_data.get('product_id'),
            length=calculation_data.get('length'),
            width=calculation_data.get('width'),
            height=calculation_data.get('height'),
            weight=calculation_data.get('weight'),
            start_postal_code=calculation_data.get('start_postal_code'),
            receiver_postal_code=calculation_data.get('receiver_postal_code'),
            is_residential=calculation_data.get('is_residential', False),
            base_fee=result['base_fee'],
            handling_fee=result['handling_fee'],
            oversize_fee=result['oversize_fee'],
            residential_fee=result['residential_fee'],
            remote_area_fee=result['remote_area_fee'],
            total_fee=result['total_fee'],
            created_at=datetime.utcnow()
        )
        
        db.session.add(history)
        db.session.commit() 

    def _get_current_pss_amount(self, surcharge_type, current_date=None):
        """获取当前PSS金额"""
        if current_date is None:
            current_date = datetime.now()
        
        print(f"获取PSS金额 - 类型: {surcharge_type}, 日期: {current_date}")
        pss_periods = surcharge_type.get('pss_periods', [])
        
        for period in pss_periods:
            start_date = datetime.strptime(period['start_date'], '%Y-%m-%d')
            end_date = datetime.strptime(period['end_date'], '%Y-%m-%d')
            
            if start_date <= current_date <= end_date:
                amount = float(period['amount'])
                print(f"找到匹配的PSS期间: {period['start_date']} 到 {period['end_date']}, 金额: ${amount}")
                return amount
                
        print("未找到匹配的PSS期间")
        return 0.0

    def _get_fee_with_pss(self, base_fee, surcharge_type, current_date=None):
        """计算包含PSS的总费用"""
        if current_date is None:
            current_date = datetime.now()
            
        print(f"\n计算PSS费用:")
        print(f"基础费用: ${base_fee}")
        print(f"当前日期: {current_date}")
        
        pss_amount = self._get_current_pss_amount(surcharge_type, current_date)
        print(f"PSS金额: ${pss_amount}")
        
        total_fee = base_fee + float(pss_amount if pss_amount else 0)
        print(f"总费用(基础费用 + PSS): ${total_fee}")
        
        return total_fee 

    def _calculate_surcharges(self, zone, weight_lb, length_in, width_in, height_in, is_residential, is_remote):
        """
        计算所有附加费用
        
        参数:
            zone: 区域编号
            weight_lb: 重量(磅)
            length_in: 长度(英寸)
            width_in: 宽度(英寸)
            height_in: 高度(英寸)
            is_residential: 是否住宅地址
            is_remote: 是否偏远地区
        返回:
            tuple: (附加费列表, 总附加费)
        """
        print(f"\n=== 计算附加费用 ===")
        print(f"区域: Zone {zone}")
        print(f"重量: {weight_lb}lb")
        print(f"尺寸: {length_in}x{width_in}x{height_in}inch")
        print(f"是否住宅地址: {is_residential}")
        print(f"是否偏远地区: {is_remote}")
        
        surcharges = []
        total_surcharges = 0.0
        
        try:
            # 验证附加费数据
            if not self.surcharges:
                print("警告: 附加费数据为空")
                return [], 0.0
                
            # 计算长度+周长
            girth = 2 * (width_in + height_in)
            total_length = length_in + girth
            print(f"长度+周长: {total_length}inch")
            
            # 1. 超大超尺寸费
            if total_length > 130 and total_length <= 165 and weight_lb < 150:
                try:
                    oversize_type = next(cat for cat in self.surcharges if '超大超尺寸' in cat['title'])
                    oversize_item = next(item for item in oversize_type['items'] 
                                      if '实际重量＜150磅' in (item.get('description', '') or item.get('name', '')))
                    
                    base_fee = float(oversize_item['fees'].get(str(zone), 0))
                    total_fee = self._get_fee_with_pss(base_fee, oversize_type)
                    
                    surcharges.append({
                        'name': f'超大超尺寸费(Zone {zone})',
                        'base_fee': base_fee,
                        'pss_fee': total_fee - base_fee,
                        'total_fee': total_fee
                    })
                    total_surcharges += total_fee
                    print(f"添加超大超尺寸费: ${total_fee}")
                except (StopIteration, KeyError, ValueError) as e:
                    print(f"计算超大超尺寸费时出错: {str(e)}")
            
            # 2. 额外处理费
            handling_type = next(cat for cat in self.surcharges if '额外处理费' in cat['title'])
            
            # 2.1 重量处理费
            if 50 < weight_lb < 150:
                try:
                    weight_item = next(item for item in handling_type['items'] if '重量' in item['name'])
                    base_fee = float(weight_item['fees'].get(str(zone), 0))
                    total_fee = self._get_fee_with_pss(base_fee, handling_type)
                    
                    surcharges.append({
                        'name': '额外处理费A(重量)',
                        'base_fee': base_fee,
                        'pss_fee': total_fee - base_fee,
                        'total_fee': total_fee
                    })
                    total_surcharges += total_fee
                    print(f"添加重量处理费: ${total_fee}")
                except (StopIteration, KeyError, ValueError) as e:
                    print(f"计算重量处理费时出错: {str(e)}")
            
            # 2.2 第二长边处理费
            if width_in > 30:
                try:
                    width_item = next(item for item in handling_type['items'] if '第二长边' in item['name'])
                    base_fee = float(width_item['fees'].get(str(zone), 0))
                    total_fee = self._get_fee_with_pss(base_fee, handling_type)
                    
                    surcharges.append({
                        'name': '额外处理费D(第二长边)',
                        'base_fee': base_fee,
                        'pss_fee': total_fee - base_fee,
                        'total_fee': total_fee
                    })
                    total_surcharges += total_fee
                    print(f"添加第二长边处理费: ${total_fee}")
                except (StopIteration, KeyError, ValueError) as e:
                    print(f"计算第二长边处理费时出错: {str(e)}")
            
            # 3. 住宅地址附加费
            if is_residential:
                try:
                    residential_type = next(cat for cat in self.surcharges if '住宅地址附加费' in cat['title'])
                    print(f"\n住宅地址附加费配置: {json.dumps(residential_type, indent=2, ensure_ascii=False)}")
                    
                    # 根据重量选择服务类型
                    service_type = 'Commercial Ground' if weight_lb > 70 else 'Home Delivery'
                    print(f"选择服务类型(基于计费重量 {weight_lb}lb): {service_type}")
                    
                    # 查找匹配的费率项
                    residential_item = None
                    for item in residential_type['items']:
                        print(f"检查费率项: {item['name']}")
                        if service_type in item['name']:
                            residential_item = item
                            print(f"找到匹配的费率项: {json.dumps(item, indent=2, ensure_ascii=False)}")
                            break
                    
                    if residential_item:
                        base_fee = float(residential_item['fees'].get('2', 0))  # 住宅地址费用统一使用Zone2的费率
                        print(f"基础费用(Zone2): ${base_fee}")
                        total_fee = self._get_fee_with_pss(base_fee, residential_type)
                        print(f"总费用(含PSS): ${total_fee}")
                        
                        surcharges.append({
                            'name': f'住宅地址附加费({service_type})',
                            'base_fee': base_fee,
                            'pss_fee': total_fee - base_fee,
                            'total_fee': total_fee
                        })
                        total_surcharges += total_fee
                        print(f"添加住宅地址附加费: ${total_fee}")
                    else:
                        print(f"未找到匹配的住宅地址附加费率: {service_type}")
                        print(f"可用的费率项: {[item['name'] for item in residential_type['items']]}")
                except (StopIteration, KeyError, ValueError) as e:
                    print(f"计算住宅地址附加费时出错: {str(e)}")
                    print(f"错误详情: {e.__class__.__name__}")
                    import traceback
                    print(traceback.format_exc())
            
            # 4. 偏远地区附加费
            if is_remote:
                try:
                    remote_type = next(cat for cat in self.surcharges if '偏远地区附加费' in cat['title'])
                    service_key = 'Ground' if weight_lb > 70 else 'Home Delivery'
                    delivery_type = 'Commercial' if not is_residential else 'Residential'
                    
                    remote_item = next(item for item in remote_type['items'] 
                                     if '远端地带' in item['name'] and 
                                     service_key in item['name'] and 
                                     delivery_type in item['name'])
                    
                    base_fee = float(remote_item['fees'].get('2', 0))  # 偏远地区费用统一使用Zone2的费率
                    total_fee = self._get_fee_with_pss(base_fee, remote_type)
                    
                    surcharges.append({
                        'name': f'偏远地区附加费({delivery_type} {service_key})',
                        'base_fee': base_fee,
                        'pss_fee': total_fee - base_fee,
                        'total_fee': total_fee
                    })
                    total_surcharges += total_fee
                    print(f"添加偏远地区附加费: ${total_fee}")
                except (StopIteration, KeyError, ValueError) as e:
                    print(f"计算偏远地区附加费时出错: {str(e)}")

            # 5. 不可发包裹费用
            try:
                # 检查是否符合不可发包裹的条件
                is_unauthorized = False
                reason = None

                # 计算长度+周长
                length_plus_girth = length_in + 2 * (width_in + height_in)
                print(f"\n=== 不可发包裹检查 ===")
                print(f"实际重量: {weight_lb}lb")
                print(f"最长边: {length_in}inch")
                print(f"长度+周长: {length_plus_girth}inch")

                # 检查不可发包裹条件
                if length_plus_girth > 165:
                    is_unauthorized = True
                    reason = 'c)最长边+周长＞165英寸'
                elif length_in > 108:
                    is_unauthorized = True
                    reason = 'b)最长边＞108英寸'
                elif weight_lb > 150:
                    is_unauthorized = True
                    reason = 'a)实重＞150磅'
                
                if is_unauthorized:
                    print(f"\n包裹不可发: {reason}")
                    unauthorized_type = next(cat for cat in self.surcharges 
                                          if cat['title'].startswith('增值服务费项目'))
                    unauthorized_items = next(item for item in unauthorized_type['items'] 
                                           if item['name'] == '5. 不可发包裹(Unauthorized)')

                    # 找到对应原因的费率项
                    fee_item = next(item for item in unauthorized_items['items'] 
                                  if reason in item['name'])
                    
                    base_fee = float(fee_item['fees'].get('2', 0))  # 不可发包裹费用统一使用Zone2的费率
                    
                    # 获取PSS费用
                    pss_amount = 0
                    current_date = datetime.now()
                    for period in unauthorized_items.get('pss_periods', []):
                        start_date = datetime.strptime(period['start_date'], '%Y-%m-%d').date()
                        end_date = datetime.strptime(period['end_date'], '%Y-%m-%d').date()
                        if start_date <= current_date.date() <= end_date:
                            pss_amount = float(period['amount'])
                            print(f"不可发包裹PSS费用: ${pss_amount}")
                            break
                    
                    total_fee = base_fee + pss_amount
                    print(f"不可发包裹总费用: ${total_fee}")
                    
                    surcharges.append({
                        'name': f'不可发包裹费({reason})',
                        'base_fee': base_fee,
                        'pss_fee': pss_amount,
                        'total_fee': total_fee
                    })
                    total_surcharges += total_fee
                    print(f"添加不可发包裹费: ${total_fee}")

            except (StopIteration, KeyError, ValueError) as e:
                print(f"计算不可发包裹费用时出错: {str(e)}")
                print(f"错误详情: {e.__class__.__name__}")
                import traceback
                print(traceback.format_exc())

            return surcharges, total_surcharges
            
        except Exception as e:
            print(f"计算附加费用时出错: {str(e)}")
            print(f"错误详情: {e.__class__.__name__}")
            import traceback
            print(traceback.format_exc())
            return [], 0.0 

    def _calculate_fuel_surcharge(self, base_amount, current_date=None):
        """
        计算燃油附加费
        
        参数:
            base_amount: 基础金额（基础运费 + 附加费总额）
            current_date: 计算日期，默认为当前日期
        返回:
            float: 燃油附加费金额
        """
        print(f"\n=== 计算燃油附加费 ===")
        print(f"基础金额: ${base_amount}")
        
        try:
            if current_date is None:
                current_date = datetime.now()
            print(f"计算日期: {current_date.strftime('%Y-%m-%d')}")
            
            # 查找燃油附加费类型
            try:
                fuel_type = next(cat for cat in self.surcharges if any(keyword in cat['title'].lower() 
                    for keyword in ['fuel', '燃油', '燃料']))
            except StopIteration:
                print("警告: 未找到燃油附加费配置")
                return 0.0
                
            # 验证燃油附加费配置
            if not fuel_type.get('items'):
                print("警告: 燃油附加费配置项为空")
                return 0.0
                
            # 获取当前适用的费率项
            try:
                current_rate = None
                for item in fuel_type['items']:
                    if 'valid_from' in item and 'valid_to' in item:
                        valid_from = datetime.strptime(item['valid_from'], '%Y-%m-%d')
                        valid_to = datetime.strptime(item['valid_to'], '%Y-%m-%d')
                        if valid_from <= current_date <= valid_to:
                            current_rate = item
                            break
                    elif 'start_date' in item and 'end_date' in item:
                        start_date = datetime.strptime(item['start_date'], '%Y-%m-%d')
                        end_date = datetime.strptime(item['end_date'], '%Y-%m-%d')
                        if start_date <= current_date <= end_date:
                            current_rate = item
                            break
                
                if not current_rate:
                    # 如果没有找到时间匹配的费率，使用默认费率
                    current_rate = next(item for item in fuel_type['items'] 
                        if 'default' in item.get('name', '').lower() or 'default' in item.get('description', '').lower())
                    print("使用默认燃油附加费率")
                
            except StopIteration:
                print("警告: 未找到适用的燃油附加费率")
                return 0.0
                
            # 获取费率和计算方式
            rate = float(current_rate.get('rate', 0))
            min_charge = float(current_rate.get('min_charge', 0))
            calculation_method = current_rate.get('calculation_method', 'percentage')
            
            print(f"费率: {rate}%")
            print(f"最低收费: ${min_charge}")
            print(f"计算方式: {calculation_method}")
            
            # 计算燃油附加费
            if calculation_method == 'percentage':
                fuel_surcharge = base_amount * (rate / 100)
            else:
                fuel_surcharge = rate
            
            # 应用最低收费
            if min_charge > 0 and fuel_surcharge < min_charge:
                print(f"应用最低收费: ${min_charge}")
                fuel_surcharge = min_charge
            
            # 应用PSS
            total_surcharge = self._get_fee_with_pss(fuel_surcharge, fuel_type)
            
            print(f"基础燃油附加费: ${fuel_surcharge:.2f}")
            print(f"最终燃油附加费(含PSS): ${total_surcharge:.2f}")
            
            return round(total_surcharge, 2)
            
        except Exception as e:
            print(f"计算燃油附加费时出错: {str(e)}")
            print(f"错误详情: {e.__class__.__name__}")
            import traceback
            print(traceback.format_exc())
            return 0.0 