from __future__ import absolute_import,unicode_literals
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


# 发送激活邮件
@shared_task # 共享任务 返回一个总是使用current_app中的任务实例的代理
def send_active_email(token, username, email):
	subject = '尚硅谷书城用户激活链接' # 标题
	message = '你好' + username  # 内容
	sender = settings.EMAIL_FROM # 显示的发件人
	receiver = [email] # 目的邮箱
	# 激活链接
	html_message = '<a href="http://127.0.0.1:8000/user/active/%s/">http://127.0.0.1:8000/user/active/</a>'%token
	# 发送邮件的链接
	send_mail(subject, message, sender,receiver, html_message=html_message)

# TODO 开启celery的命令
# celery -A bookstore worker -l info
