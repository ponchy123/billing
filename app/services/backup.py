import os
import subprocess
from datetime import datetime
import shutil
import gzip
from flask import current_app
from ..utils.logger import logger

class BackupService:
    """备份服务类"""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
            
    def init_app(self, app):
        """初始化备份服务"""
        self.backup_dir = os.path.join(app.root_path, 'backups')
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
            
    def create_backup(self, description=None):
        """创建备份"""
        try:
            # 生成备份文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = f'backup_{timestamp}.sql.gz'
            backup_path = os.path.join(self.backup_dir, backup_file)
            
            # 获取数据库配置
            db_url = current_app.config['SQLALCHEMY_DATABASE_URI']
            if db_url.startswith('sqlite:///'):
                # SQLite数据库备份
                db_path = db_url.replace('sqlite:///', '')
                with open(db_path, 'rb') as f_in:
                    with gzip.open(backup_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            else:
                # MySQL/PostgreSQL数据库备份
                # TODO: 实现其他数据库的备份逻辑
                pass
                
            # 记录备份信息
            backup_info = {
                'file': backup_file,
                'description': description,
                'created_at': datetime.now()
            }
            
            # 记录日志
            logger.log_operation(
                'create_backup',
                None,
                'database',
                backup_file,
                True,
                description
            )
            
            return True, backup_info
            
        except Exception as e:
            # 记录日志
            logger.log_operation(
                'create_backup',
                None,
                'database',
                None,
                False,
                str(e)
            )
            return False, str(e)
            
    def restore_backup(self, backup_file):
        """恢复备份"""
        try:
            backup_path = os.path.join(self.backup_dir, backup_file)
            if not os.path.exists(backup_path):
                return False, "备份文件不存在"
                
            # 获取数据库配置
            db_url = current_app.config['SQLALCHEMY_DATABASE_URI']
            if db_url.startswith('sqlite:///'):
                # SQLite数据库恢复
                db_path = db_url.replace('sqlite:///', '')
                with gzip.open(backup_path, 'rb') as f_in:
                    with open(db_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            else:
                # MySQL/PostgreSQL数据库恢复
                # TODO: 实现其他数据库的恢复逻辑
                pass
                
            # 记录日志
            logger.log_operation(
                'restore_backup',
                None,
                'database',
                backup_file,
                True,
                None
            )
            
            return True, "备份恢复成功"
            
        except Exception as e:
            # 记录日志
            logger.log_operation(
                'restore_backup',
                None,
                'database',
                backup_file,
                False,
                str(e)
            )
            return False, str(e)
            
    def delete_backup(self, backup_file):
        """删除备份"""
        try:
            backup_path = os.path.join(self.backup_dir, backup_file)
            if not os.path.exists(backup_path):
                return False, "备份文件不存在"
                
            # 删除备份文件
            os.remove(backup_path)
            
            # 记录日志
            logger.log_operation(
                'delete_backup',
                None,
                'database',
                backup_file,
                True,
                None
            )
            
            return True, "备份删除成功"
            
        except Exception as e:
            # 记录日志
            logger.log_operation(
                'delete_backup',
                None,
                'database',
                backup_file,
                False,
                str(e)
            )
            return False, str(e)
            
    def list_backups(self):
        """获取备份列表"""
        try:
            backups = []
            for file in os.listdir(self.backup_dir):
                if file.endswith('.sql.gz'):
                    backup_path = os.path.join(self.backup_dir, file)
                    backup_info = {
                        'file': file,
                        'size': os.path.getsize(backup_path),
                        'created_at': datetime.fromtimestamp(
                            os.path.getctime(backup_path)
                        )
                    }
                    backups.append(backup_info)
            return sorted(backups, key=lambda x: x['created_at'], reverse=True)
        except Exception:
            return [] 