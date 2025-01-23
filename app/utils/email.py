from threading import Thread
from flask import current_app
from flask_mail import Message
from app import mail
from app.utils.exceptions import EmailError

def send_async_email(app, msg):
    """异步发送邮件"""
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            raise EmailError(f'发送邮件失败: {str(e)}')

def send_email(subject, recipients, text_body, html_body, sender=None, attachments=None):
    """
    发送邮件
    
    参数:
        subject: 邮件主题
        recipients: 收件人列表
        text_body: 纯文本内容
        html_body: HTML内容
        sender: 发件人，默认使用配置中的默认发件人
        attachments: 附件列表，每个附件是一个(文件名, MIME类型, 文件数据)的元组
    """
    if not sender:
        sender = current_app.config['MAIL_DEFAULT_SENDER']
        
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    
    if attachments:
        for filename, mimetype, data in attachments:
            msg.attach(filename=filename,
                      content_type=mimetype,
                      data=data)
    
    Thread(target=send_async_email,
           args=(current_app._get_current_object(), msg)).start() 