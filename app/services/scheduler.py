from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from ..utils.logger import logger
from ..services.backup import BackupService

class SchedulerService:
    """调度服务类"""
    
    def __init__(self, app=None):
        self.app = app
        self.scheduler = None
        if app is not None:
            self.init_app(app)
            
    def init_app(self, app):
        """初始化调度器"""
        try:
            # 配置调度器
            jobstores = {
                'default': SQLAlchemyJobStore(url=app.config['SQLALCHEMY_DATABASE_URI'])
            }
            executors = {
                'default': ThreadPoolExecutor(20)
            }
            job_defaults = {
                'coalesce': False,
                'max_instances': 3
            }
            
            # 创建调度器
            self.scheduler = BackgroundScheduler(
                jobstores=jobstores,
                executors=executors,
                job_defaults=job_defaults,
                timezone='UTC'
            )
            
            # 添加默认任务
            self.add_default_jobs()
            
            # 启动调度器
            self.scheduler.start()
            
            # 记录日志
            logger.log_info('Scheduler started successfully')
            
        except Exception as e:
            logger.log_error(f'Failed to start scheduler: {str(e)}')
            
    def add_default_jobs(self):
        """添加默认任务"""
        try:
            # 添加数据库备份任务
            self.scheduler.add_job(
                func=BackupService.create_backup,
                trigger=CronTrigger(hour=2),  # 每天凌晨2点执行
                id='database_backup',
                name='Database Backup',
                replace_existing=True
            )
            
            # 记录日志
            logger.log_info('Default jobs added successfully')
            
        except Exception as e:
            logger.log_error(f'Failed to add default jobs: {str(e)}')
            
    def add_job(self, func, trigger, id, name, **kwargs):
        """添加任务"""
        try:
            self.scheduler.add_job(
                func=func,
                trigger=trigger,
                id=id,
                name=name,
                **kwargs
            )
            
            # 记录日志
            logger.log_info(f'Job {name} added successfully')
            return True
            
        except Exception as e:
            logger.log_error(f'Failed to add job {name}: {str(e)}')
            return False
            
    def remove_job(self, job_id):
        """移除任务"""
        try:
            self.scheduler.remove_job(job_id)
            
            # 记录日志
            logger.log_info(f'Job {job_id} removed successfully')
            return True
            
        except Exception as e:
            logger.log_error(f'Failed to remove job {job_id}: {str(e)}')
            return False
            
    def get_jobs(self):
        """获取所有任务"""
        try:
            jobs = self.scheduler.get_jobs()
            return [(job.id, job.name, str(job.trigger)) for job in jobs]
            
        except Exception as e:
            logger.log_error(f'Failed to get jobs: {str(e)}')
            return []
            
    def pause_job(self, job_id):
        """暂停任务"""
        try:
            self.scheduler.pause_job(job_id)
            
            # 记录日志
            logger.log_info(f'Job {job_id} paused successfully')
            return True
            
        except Exception as e:
            logger.log_error(f'Failed to pause job {job_id}: {str(e)}')
            return False
            
    def resume_job(self, job_id):
        """恢复任务"""
        try:
            self.scheduler.resume_job(job_id)
            
            # 记录日志
            logger.log_info(f'Job {job_id} resumed successfully')
            return True
            
        except Exception as e:
            logger.log_error(f'Failed to resume job {job_id}: {str(e)}')
            return False
            
    def modify_job(self, job_id, **changes):
        """修改任务"""
        try:
            self.scheduler.modify_job(job_id, **changes)
            
            # 记录日志
            logger.log_info(f'Job {job_id} modified successfully')
            return True
            
        except Exception as e:
            logger.log_error(f'Failed to modify job {job_id}: {str(e)}')
            return False
            
    def shutdown(self):
        """关闭调度器"""
        try:
            if self.scheduler:
                self.scheduler.shutdown()
                
            # 记录日志
            logger.log_info('Scheduler shutdown successfully')
            
        except Exception as e:
            logger.log_error(f'Failed to shutdown scheduler: {str(e)}') 