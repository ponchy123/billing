import os
import pandas as pd
from datetime import datetime
from app.utils.exceptions import ExportError

class ExportService:
    """导出服务类"""
    
    EXPORT_DIR = 'exports'
    
    @classmethod
    def ensure_export_dir(cls):
        """确保导出目录存在"""
        if not os.path.exists(cls.EXPORT_DIR):
            os.makedirs(cls.EXPORT_DIR)
    
    @classmethod
    def get_export_path(cls, filename):
        """获取导出文件路径"""
        cls.ensure_export_dir()
        return os.path.join(cls.EXPORT_DIR, filename)
    
    @classmethod
    def export_data(cls, data, filename, data_type):
        """
        导出数据到Excel文件
        
        参数:
            data: 要导出的数据
            filename: 导出文件名
            data_type: 数据类型，用于确定导出格式
        """
        try:
            filepath = cls.get_export_path(filename)
            
            if data_type == 'customers':
                return cls._export_customers(data, filepath)
            elif data_type == 'calculation_history':
                return cls._export_calculation_history(data, filepath)
            elif data_type == 'calculation':
                return cls._export_calculation(data, filepath)
            else:
                df = pd.DataFrame(data)
                df.to_excel(filepath, index=False, engine='openpyxl')
                return filepath
                
        except Exception as e:
            raise ExportError(f'导出失败: {str(e)}')
    
    @classmethod
    def _export_customers(cls, data, filepath):
        """导出客户列表"""
        df = pd.DataFrame(data)
        df = df.rename(columns={
            'username': '用户名',
            'created_at': '创建时间',
            'last_active_at': '最后活动时间',
            'total_calculations': '计算次数',
            'total_amount': '总金额'
        })
        df.to_excel(filepath, index=False, engine='openpyxl')
        return filepath
    
    @classmethod
    def _export_calculation_history(cls, data, filepath):
        """导出计算历史"""
        df = pd.DataFrame(data)
        df = df.rename(columns={
            'created_at': '计算时间',
            'product_name': '产品',
            'length': '长度(cm)',
            'width': '宽度(cm)',
            'height': '高度(cm)',
            'weight': '重量(kg)',
            'zone': '区域',
            'base_fee': '基本费用',
            'handling_fee': '操作费',
            'oversize_fee': '超大件费用',
            'residential_fee': '住宅配送费',
            'remote_area_fee': '偏远地区费',
            'total_fee': '总费用'
        })
        df.to_excel(filepath, index=False, engine='openpyxl')
        return filepath
    
    @classmethod
    def _export_calculation(cls, data, filepath):
        """导出单个计算结果"""
        # 基本信息
        basic_info = pd.DataFrame([{
            '长度(cm)': data['length'],
            '宽度(cm)': data['width'],
            '高度(cm)': data['height'],
            '重量(kg)': data['weight'],
            '区域': data['zone']
        }])
        
        # 费用明细
        fee_details = pd.DataFrame([{
            '基本费用': data['base_fee'],
            '操作费': data['handling_fee'],
            '超大件费用': data['oversize_fee'],
            '住宅配送费': data['residential_fee'],
            '偏远地区费': data['remote_area_fee'],
            '总费用': data['total_fee']
        }])
        
        # 创建Excel写入器
        writer = pd.ExcelWriter(filepath, engine='openpyxl')
        
        # 写入不同的sheet
        basic_info.to_excel(writer, sheet_name='基本信息', index=False)
        fee_details.to_excel(writer, sheet_name='费用明细', index=False)
        
        # 保存文件
        writer.close()
        return filepath 