from __future__ import absolute_import,unicode_literals
import os
from celery import Celery

# 为celery设置django默认的模块信息与项目的配置信息
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookstore.settings')

# 实例化celery,(应用,代理的redis信息)
app = Celery('bookstore',broker='redis://127.0.0.1:6379/2')

# 配置对象到子进程,namespace='CELERY'-->指celery相关配置的钥匙
app.config_from_object('django.conf:settings', namespace='CELERY')

# 从所有注册的django项目的应用中加载任务模块
app.autodiscover_tasks()

# 开启debug模式,可以显示信息
@app.task(bind=True)
def debug_task(self):
	print('Request:{0!r}'.format(self.request))