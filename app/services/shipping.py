from decimal import Decimal
from ..utils.string_utils import is_valid_postcode
from ..utils.error_handlers import ErrorHandlers

class ShippingService:
    """运输服务类"""
    
    @staticmethod
    @ErrorHandlers.handle_validation
    def validate_shipping_info(length, width, height, weight, start_postcode, receiver_postcode=None):
        """
        验证运输信息
        
        Args:
            length: 长度(厘米)
            width: 宽度(厘米)
            height: 高度(厘米)
            weight: 重量(千克)
            start_postcode: 起始邮编
            receiver_postcode: 收件邮编(可选)
            
        Returns:
            tuple: (是否验证通过, 错误信息)
        """
        # 验证尺寸
        dimensions = [
            ('长度', length),
            ('宽度', width),
            ('高度', height)
        ]
        for name, value in dimensions:
            if not value:
                return False, f"{name}不能为空"
            try:
                value = float(value)
                if value <= 0:
                    return False, f"{name}必须大于0"
            except ValueError:
                return False, f"{name}必须是数字"
                
        # 验证重量
        if not weight:
            return False, "重量不能为空"
        try:
            weight = float(weight)
            if weight <= 0:
                return False, "重量必须大于0"
        except ValueError:
            return False, "重量必须是数字"
            
        # 验证邮编
        if not start_postcode:
            return False, "起始邮编不能为空"
        if not is_valid_postcode(start_postcode):
            return False, "起始邮编格式不正确"
            
        if receiver_postcode and not is_valid_postcode(receiver_postcode):
            return False, "收件邮编格式不正确"
            
        return True, None
        
    @staticmethod
    @ErrorHandlers.handle_validation
    def validate_zone_info(zone, remote_level=None):
        """
        验证分区信息
        
        Args:
            zone: 分区号
            remote_level: 偏远等级(可选)
            
        Returns:
            tuple: (是否验证通过, 错误信息)
        """
        # 验证分区
        if zone is None:
            return False, "分区不能为空"
        try:
            zone = int(zone)
            if zone not in [2, 3, 4, 5, 6, 7, 8, 9, 17]:
                return False, "分区不正确"
        except ValueError:
            return False, "分区必须是数字"
            
        # 验证偏远等级
        if remote_level is not None:
            try:
                remote_level = int(remote_level)
                if remote_level not in [1, 2]:  # 1=一级偏远, 2=二级偏远
                    return False, "偏远等级不正确"
            except ValueError:
                return False, "偏远等级必须是数字"
                
        return True, None 