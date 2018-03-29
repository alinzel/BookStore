from django.db import models


# 抽象一个基类，一些数据库表存在的相同字段
class BaseModels(models.Model):
	# auto_now_add为添加时的时间，更新对象时不会有变动。
	create_at = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
	# auto_now无论是你添加还是修改对象，时间为你添加或者修改的时间。
	update_at = models.DateTimeField(verbose_name='更新时间', auto_now=True)
	is_delete = models.BooleanField(verbose_name='是否删除', default=False)

	class Meta:
		abstract = True  # 定义此继承方式为抽象基类继承
