from app.extensions import db
from datetime import datetime

class PostalZone(db.Model):
    """邮编区域"""
    __tablename__ = 'postal_zones'
    
    id = db.Column(db.Integer, primary_key=True)
    start_code = db.Column(db.String(100), nullable=False, comment='起始邮编')
    end_code = db.Column(db.String(100), nullable=True, comment='结束邮编')
    zone_name = db.Column(db.String(100), nullable=True, comment='区域名称')
    type = db.Column(db.String(50), nullable=False, comment='类型')
    excel_content = db.Column(db.Text, nullable=True, comment='Excel文件内容')
    file_name = db.Column(db.String(255), nullable=True, comment='文件名')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<PostalZone {self.id}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'start_code': self.start_code,
            'end_code': self.end_code,
            'zone_name': self.zone_name,
            'type': self.type,
            'file_name': self.file_name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 