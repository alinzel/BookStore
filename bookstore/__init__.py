from __future__ import absolute_import, unicode_literals
from .celery import app as celery_app

import pymysql

pymysql.install_as_MySQLdb()

# 配置celeryapp 使其可以导入 TODO 确保当Django开始让share_task执行任务时候,确保应用程序一直是入口,得以被执行
__all__ = ['celery_app']

