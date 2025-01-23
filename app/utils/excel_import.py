import pandas as pd
import os
from datetime import datetime
from werkzeug.utils import secure_filename
import logging

logger = logging.getLogger(__name__)

class ExcelImporter:
    """Excel导入处理器"""
    
    def __init__(self, file):
        self.file = file
        self.temp_path = None
        
    def __enter__(self):
        # 保存临时文件
        filename = secure_filename(self.file.filename)
        # 使用项目的temp目录
        temp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'temp')
        # 确保temp目录存在
        os.makedirs(temp_dir, exist_ok=True)
        self.temp_path = os.path.join(temp_dir, filename)
        self.file.save(self.temp_path)
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        # 清理临时文件
        if self.temp_path and os.path.exists(self.temp_path):
            try:
                os.remove(self.temp_path)
            except Exception as e:
                logger.warning(f"清理临时文件失败: {str(e)}")
            
    @staticmethod
    def validate_file(file):
        """验证上传的文件"""
        if not file:
            raise ValueError('未上传文件')
            
        if not file.filename:
            raise ValueError('文件名无效')
            
        if not file.filename.lower().endswith(('.xls', '.xlsx')):
            raise ValueError('只支持Excel文件格式(.xls, .xlsx)')
    
    def process_basic_info(self, df):
        """处理基本信息sheet"""
        product_info = {
            'product': 'FEDEX GROUND',
            'carrier': 'FEDEX',
            'start_date': pd.to_datetime('2025/01/06'),
            'dim': 250.0,
            'unit': 'LB'
        }
        
        # 遍历所有行查找关键信息
        for idx, row in df.iterrows():
            if pd.notna(row.iloc[0]):
                key = str(row.iloc[0]).strip()
                if key.startswith('DIM'):
                    product_info['dim'] = float(str(row.iloc[1]).strip()) if pd.notna(row.iloc[1]) else 250.0
                elif key.startswith('产品') or key.startswith('Product'):
                    product_info['product'] = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else 'FEDEX GROUND'
                elif key.startswith('服务商') or key.startswith('Carrier'):
                    product_info['carrier'] = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else 'FEDEX'
                elif key.startswith('开始有效期') or key.startswith('Start Date'):
                    date_str = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else '2025/01/06'
                    try:
                        product_info['start_date'] = pd.to_datetime(date_str)
                    except:
                        product_info['start_date'] = pd.to_datetime('2025/01/06')
                elif key.startswith('UNIT') or key.startswith('单位'):
                    product_info['unit'] = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else 'LB'
                    
        return product_info
    
    def process_zone_rates(self, df):
        """处理区域费率sheet"""
        print("\n=== 处理区域费率sheet ===")
        zone_rates = []
        
        # 查找表头行
        header_row = None
        for idx, row in df.iterrows():
            if row.astype(str).str.contains('Zone|zone|区域', case=False).any():
                header_row = idx
                print(f"找到表头行: {idx}")
                print(f"表头内容: {row.tolist()}")
                break
        
        if header_row is not None:
            # 使用表头行后的数据
            df_rates = df.iloc[header_row + 1:]
            df_rates = df_rates.reset_index(drop=True)
            print(f"\n处理费率数据，共 {len(df_rates)} 行")
        else:
            # 如果没有找到表头，假设整个sheet都是数据
            df_rates = df
            print("\n警告: 未找到表头行，使用整个sheet作为数据")
            print(f"数据行数: {len(df_rates)}")
        
        # 验证必要的列是否存在
        required_columns = ['weight', 'Zone2', 'Zone3', 'Zone4', 'Zone5', 'Zone6', 'Zone7', 'Zone8']
        missing_columns = []
        for col in required_columns:
            if not any(str(header).lower().strip() == col.lower() for header in df_rates.columns):
                missing_columns.append(col)
        
        if missing_columns:
            raise ValueError(f"费率表缺少必要的列: {', '.join(missing_columns)}")
        
        # 处理费率数据
        for idx, row in df_rates.iterrows():
            if pd.notna(row.iloc[0]):
                try:
                    weight = float(str(row.iloc[0]).strip())
                    if weight <= 0:
                        print(f"警告: 第 {idx+1} 行重量必须大于0: {weight}")
                        continue
                        
                    rate_data = {'weight': weight}
                    
                    # 获取各个区域的费率
                    for col in range(1, min(9, len(row))):  # 最多8个区域
                        if pd.notna(row.iloc[col]):
                            try:
                                rate = float(str(row.iloc[col]).strip())
                                if rate < 0:
                                    print(f"警告: 第 {idx+1} 行 Zone{col} 的费率不能为负数: {rate}")
                                    continue
                                rate_data[f'Zone{col}'] = rate
                            except:
                                print(f"警告: 第 {idx+1} 行 Zone{col} 的费率格式无效: {row.iloc[col]}")
                                continue
                    
                    # 验证是否包含所有必要的区域费率
                    missing_zones = []
                    for zone in range(2, 9):
                        zone_key = f'Zone{zone}'
                        if zone_key not in rate_data:
                            missing_zones.append(zone_key)
                    
                    if missing_zones:
                        print(f"警告: 第 {idx+1} 行缺少以下区域的费率: {', '.join(missing_zones)}")
                        continue
                    
                    # 打印处理结果
                    if 85 <= weight <= 95:  # 只打印85-95磅范围的费率
                        print(f"\n处理第 {idx+1} 行:")
                        print(f"重量: {weight}lb")
                        print("区域费率:")
                        for zone_key, rate in rate_data.items():
                            if zone_key != 'weight':
                                print(f"- {zone_key}: ${rate}")
                    
                    zone_rates.append(rate_data)
                except Exception as e:
                    print(f"警告: 处理第 {idx+1} 行时出错: {str(e)}")
                    continue
        
        if not zone_rates:
            raise ValueError("没有有效的费率数据")
        
        # 检查是否有90磅的费率
        has_90_lb = any(abs(float(rate['weight']) - 90) < 0.01 for rate in zone_rates)
        if not has_90_lb:
            print("\n警告: 费率表中没有90磅的费率")
        
        # 按重量排序
        zone_rates.sort(key=lambda x: float(x['weight']))
        
        print(f"\n总共处理了 {len(zone_rates)} 条费率数据")
        return zone_rates
    
    def process_surcharges(self, df):
        """处理附加费用sheet"""
        print("\n=== 处理附加费用sheet ===")
        surcharges = []
        current_category = None
        current_item = None
        
        for idx, row in df.iterrows():
            try:
                if not pd.notna(row.iloc[0]):
                    continue
                    
                first_cell = str(row.iloc[0]).strip()
                
                # 检查是否是分类标题
                if any(keyword in first_cell.lower() for keyword in ['surcharge', '附加费', '费用']):
                    print(f"\n处理分类: {first_cell}")
                    current_category = {
                        'title': first_cell,
                        'not_applicable': '不叠加' in first_cell,
                        'items': [],
                        'pss_periods': []
                    }
                    surcharges.append(current_category)
                    current_item = None
                    continue
                
                # 检查是否是PSS时间段
                if current_category and 'pss' in first_cell.lower():
                    if len(row) >= 4 and pd.notna(row.iloc[1]) and pd.notna(row.iloc[2]) and pd.notna(row.iloc[3]):
                        try:
                            start_date = pd.to_datetime(row.iloc[1]).strftime('%Y-%m-%d')
                            end_date = pd.to_datetime(row.iloc[2]).strftime('%Y-%m-%d')
                            amount = float(str(row.iloc[3]).strip())
                            
                            print(f"添加PSS时间段: {start_date} 到 {end_date}, 金额: ${amount}")
                            current_category['pss_periods'].append({
                                'start_date': start_date,
                                'end_date': end_date,
                                'amount': amount
                            })
                        except Exception as e:
                            print(f"警告: 处理PSS时间段时出错: {str(e)}")
                    continue
                
                # 检查是否是费用项
                if current_category and pd.notna(row.iloc[1]):
                    try:
                        # 判断是否是子项目
                        is_sub_item = first_cell.startswith(('a)', 'b)', 'c)', 'd)', 'e)'))
                        
                        # 处理费率数据
                        fees = {}
                        for col in range(1, min(9, len(row))):
                            if pd.notna(row.iloc[col]):
                                try:
                                    rate = float(str(row.iloc[col]).strip())
                                    if rate >= 0:  # 费率不能为负数
                                        fees[str(col + 1)] = rate
                                except:
                                    continue
                        
                        item = {
                            'name': first_cell,
                            'fees': fees
                        }
                        
                        # 添加说明文字
                        if len(row) > len(fees) + 1 and pd.notna(row.iloc[len(fees) + 1]):
                            item['description'] = str(row.iloc[len(fees) + 1]).strip()
                        
                        if is_sub_item and current_item:
                            # 如果是子项目，添加到当前主项目下
                            if 'items' not in current_item:
                                current_item['items'] = []
                            current_item['items'].append(item)
                            print(f"添加子项目: {first_cell}")
                        else:
                            # 如果是主项目，添加到当前分类下
                            current_category['items'].append(item)
                            current_item = item
                            print(f"添加主项目: {first_cell}")
                            
                    except Exception as e:
                        print(f"警告: 处理费用项时出错: {str(e)}")
                        continue
            
            except Exception as e:
                print(f"警告: 处理第 {idx+1} 行时出错: {str(e)}")
                continue
        
        # 验证处理结果
        if not surcharges:
            print("警告: 未找到任何附加费用数据")
            return []
            
        # 验证每个分类
        for category in surcharges:
            if not category['items']:
                print(f"警告: 分类 '{category['title']}' 没有任何费用项")
            else:
                print(f"\n分类 '{category['title']}':")
                print(f"- 费用项数量: {len(category['items'])}")
                print(f"- PSS时间段数量: {len(category['pss_periods'])}")
                
        return surcharges
    
    def process_excel(self):
        """处理Excel文件"""
        try:
            # 读取所有sheet
            dfs = pd.read_excel(self.temp_path, sheet_name=None)
            
            if len(dfs) < 3:
                raise ValueError('Excel文件必须包含3个工作表')
            
            # 获取三个DataFrame
            df_basic = list(dfs.values())[0]  # 基本信息sheet
            df_rates = list(dfs.values())[1]  # 区域费率sheet
            df_surcharges = list(dfs.values())[2]  # 附加费用sheet
            
            # 处理每个sheet
            product_info = self.process_basic_info(df_basic)
            zone_rates = self.process_zone_rates(df_rates)
            surcharges = self.process_surcharges(df_surcharges)
            
            # 返回处理结果
            return {
                'product_info': product_info,
                'zone_rates': zone_rates,
                'surcharges': surcharges
            }
            
        except Exception as e:
            logger.error(f"处理Excel文件失败: {str(e)}", exc_info=True)
            raise ValueError(f'处理Excel文件失败: {str(e)}')