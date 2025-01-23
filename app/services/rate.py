from decimal import Decimal
import decimal
from ..utils.date_utils import is_valid_date
from ..utils.error_handlers import ErrorHandlers

class RateService:
    """费率服务类"""
    
    @staticmethod
    @ErrorHandlers.handle_validation
    def validate_rate_info(rate, start_date, end_date):
        """
        验证费率信息
        
        Args:
            rate: 费率值
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            tuple: (是否验证通过, 错误信息)
        """
        # 验证费率
        if rate is None:
            return False, "费率不能为空"
        try:
            rate = Decimal(str(rate))
            if rate < 0:
                return False, "费率不能小于0"
        except (ValueError, decimal.InvalidOperation):
            return False, "费率格式不正确"
            
        # 验证日期
        if not start_date:
            return False, "开始日期不能为空"
        if not is_valid_date(start_date):
            return False, "开始日期格式不正确"
            
        if not end_date:
            return False, "结束日期不能为空"
        if not is_valid_date(end_date):
            return False, "结束日期格式不正确"
            
        # 验证日期范围
        if start_date > end_date:
            return False, "结束日期必须大于开始日期"
            
        return True, None 