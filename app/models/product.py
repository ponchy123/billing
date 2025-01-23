from app.extensions import db
from datetime import datetime
import json

class Product(db.Model):
    """产品"""
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, comment='产品名称')
    carrier = db.Column(db.String(100), nullable=False, comment='服务商')
    start_date = db.Column(db.Date, nullable=False, comment='开始有效期')
    volume_weight_factor = db.Column(db.Float, nullable=False, default=250.0, comment='体积重系数')
    unit = db.Column(db.String(10), nullable=False, default='LB', comment='重量单位')
    zone_rates = db.Column(db.Text, nullable=True, comment='区域费率')
    surcharges = db.Column(db.Text, nullable=True, comment='附加费用')
    status = db.Column(db.String(20), nullable=False, default='active', comment='状态')
    dim = db.Column(db.Float, nullable=True, comment='体积重量计算系数')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, **kwargs):
        """初始化产品"""
        super(Product, self).__init__(**kwargs)
        if 'volume_weight_factor' not in kwargs:
            self.volume_weight_factor = 250.0  # 设置默认值
        if 'unit' not in kwargs:
            self.unit = 'LB'  # 设置默认值
        if 'status' not in kwargs:
            self.status = 'active'  # 设置默认值
    
    def __repr__(self):
        return f'<Product {self.name}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'carrier': self.carrier,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'volume_weight_factor': self.volume_weight_factor,
            'unit': self.unit,
            'zone_rates': self.zone_rates,
            'surcharges': self.surcharges,
            'status': self.status,
            'dim': self.dim,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def validate_zone_rates(self):
        """验证费率表数据"""
        print(f"\n=== 验证产品 {self.name} 的费率表数据 ===")
        try:
            # 解析费率表数据
            if isinstance(self.zone_rates, str):
                zone_rates = json.loads(self.zone_rates)
            else:
                zone_rates = self.zone_rates
            
            if not zone_rates:
                print("错误: 费率表为空")
                return False
            
            print(f"费率表条目数: {len(zone_rates)}")
            
            # 检查数据结构
            print("\n检查数据结构:")
            for idx, rate in enumerate(zone_rates):
                if 'weight' not in rate:
                    print(f"错误: 第 {idx+1} 条数据缺少weight字段")
                    return False
                
                weight = float(rate['weight'])
                if 85 <= weight <= 95:  # 只打印85-95磅范围的费率
                    print(f"\n第 {idx+1} 条数据:")
                    print(f"重量: {weight}lb")
                    print("区域费率:")
                    for key, value in rate.items():
                        if key != 'weight':
                            print(f"- {key}: ${value}")
            
            # 检查是否按重量排序
            weights = [float(rate['weight']) for rate in zone_rates]
            is_sorted = all(weights[i] <= weights[i+1] for i in range(len(weights)-1))
            if not is_sorted:
                print("\n警告: 费率表未按重量排序")
            
            # 检查区域费率的完整性
            zones = set()
            for rate in zone_rates:
                for key in rate.keys():
                    if key.startswith('Zone'):
                        zones.add(key)
            
            print(f"\n包含的区域: {sorted(list(zones))}")
            
            # 检查90磅的费率
            print("\n检查90磅的费率:")
            exact_90 = next((rate for rate in zone_rates if abs(float(rate['weight']) - 90) < 0.01), None)
            if exact_90:
                print("找到90磅的精确费率:")
                for key, value in exact_90.items():
                    if key != 'weight':
                        print(f"- {key}: ${value}")
            else:
                print("未找到90磅的精确费率")
                # 查找最接近的费率
                closest = min(zone_rates, key=lambda x: abs(float(x['weight']) - 90))
                print(f"最接近的费率(重量: {closest['weight']}lb):")
                for key, value in closest.items():
                    if key != 'weight':
                        print(f"- {key}: ${value}")
            
            return True
            
        except Exception as e:
            print(f"验证费率表时出错: {str(e)}")
            print(f"错误详情: {e.__class__.__name__}")
            import traceback
            print(traceback.format_exc())
            return False 
    
    def from_dict(self, data):
        """从字典更新属性"""
        fields = ['name', 'carrier', 'unit', 'dim', 'status']
        for field in fields:
            if field in data:
                setattr(self, field, data[field])
                
        # 处理日期字段
        if 'start_date' in data:
            if isinstance(data['start_date'], str):
                if '/' in data['start_date']:
                    self.start_date = datetime.strptime(data['start_date'], '%Y/%m/%d').date()
                else:
                    self.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
            elif isinstance(data['start_date'], datetime):
                self.start_date = data['start_date'].date()
                
        # 处理区域费率
        if 'zone_rates' in data:
            if isinstance(data['zone_rates'], str):
                self.zone_rates = data['zone_rates']
            else:
                self.zone_rates = json.dumps(data['zone_rates'], ensure_ascii=False)
                
        # 处理附加费用
        if 'surcharges' in data:
            if isinstance(data['surcharges'], str):
                self.surcharges = data['surcharges']
            else:
                self.surcharges = json.dumps(data['surcharges'], ensure_ascii=False) 