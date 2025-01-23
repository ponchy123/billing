from datetime import datetime
from app.extensions import db

class CalculationHistory(db.Model):
    """计算历史记录"""
    __tablename__ = 'calculation_histories'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    # 包裹信息
    length = db.Column(db.Float, nullable=False, comment='长度(cm)')
    width = db.Column(db.Float, nullable=False, comment='宽度(cm)')
    height = db.Column(db.Float, nullable=False, comment='高度(cm)')
    weight = db.Column(db.Float, nullable=False, comment='重量(kg)')
    
    # 邮编信息
    start_postal_code = db.Column(db.String(5), nullable=False, comment='起始邮编')
    receiver_postal_code = db.Column(db.String(5), nullable=False, comment='收件邮编')
    is_residential = db.Column(db.Boolean, default=False, comment='是否住宅配送')
    
    # 费用信息
    base_fee = db.Column(db.Float, nullable=False, comment='基本费用')
    handling_fee = db.Column(db.Float, nullable=False, comment='操作费')
    oversize_fee = db.Column(db.Float, nullable=False, comment='超大件费用')
    residential_fee = db.Column(db.Float, nullable=False, comment='住宅配送费')
    remote_area_fee = db.Column(db.Float, nullable=False, comment='偏远地区费')
    total_fee = db.Column(db.Float, nullable=False, comment='总费用')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    
    # 关联关系
    user = db.relationship('User', backref='calculations')
    product = db.relationship('Product', backref='calculations')
    
    def __repr__(self):
        return f'<CalculationHistory {self.id}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'length': self.length,
            'width': self.width,
            'height': self.height,
            'weight': self.weight,
            'start_postal_code': self.start_postal_code,
            'receiver_postal_code': self.receiver_postal_code,
            'is_residential': self.is_residential,
            'base_fee': self.base_fee,
            'handling_fee': self.handling_fee,
            'oversize_fee': self.oversize_fee,
            'residential_fee': self.residential_fee,
            'remote_area_fee': self.remote_area_fee,
            'total_fee': self.total_fee,
            'created_at': self.created_at.isoformat()
        }

# 为了兼容性，将 CalculationHistory 作为 Calculation 的别名
Calculation = CalculationHistory 