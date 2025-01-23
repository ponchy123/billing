import os
import pandas as pd
from datetime import datetime
from app.utils.exceptions import ExportError

class ExportUtil:
    """导出工具类"""
    
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
    def export_calculation(cls, history, filename):
        """
        导出计算结果
        
        参数:
            history: 计算历史记录
            filename: 导出文件名
        返回:
            str: 导出文件路径
        """
        try:
            filepath = cls.get_export_path(filename)
            
            # 基本信息
            basic_info = pd.DataFrame([{
                '长度(cm)': history.length,
                '宽度(cm)': history.width,
                '高度(cm)': history.height,
                '重量(kg)': history.weight,
                '区域': history.zone
            }])
            
            # 费用明细
            fee_details = pd.DataFrame([{
                '基本费用': history.base_fee,
                '操作费': history.handling_fee,
                '超大件费用': history.oversize_fee,
                '住宅配送费': history.residential_fee,
                '偏远地区费': history.remote_area_fee,
                '总费用': history.total_fee
            }])
            
            # 创建Excel写入器
            writer = pd.ExcelWriter(filepath, engine='openpyxl')
            
            # 写入不同的sheet
            basic_info.to_excel(writer, sheet_name='基本信息', index=False)
            fee_details.to_excel(writer, sheet_name='费用明细', index=False)
            
            # 保存文件
            writer.close()
            return filepath
            
        except Exception as e:
            raise ExportError(f'导出失败: {str(e)}') 