from datetime import datetime
from app.extensions import db

class FuelRate(db.Model):
    __tablename__ = 'fuel_rates'

    id = db.Column(db.Integer, primary_key=True)
    rate = db.Column(db.Float, nullable=False, comment='燃油费率(%)')
    effective_date = db.Column(db.DateTime, nullable=False, comment='生效日期')
    expiry_date = db.Column(db.DateTime, nullable=True, comment='失效日期')
    is_active = db.Column(db.Boolean, nullable=False, default=True, comment='是否启用')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'rate': self.rate,
            'effective_date': self.effective_date.isoformat(),
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        } 