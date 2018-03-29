from django.db import models
from db.Base_DB import BaseModels
from tinymce.models import HTMLField
from books.enums import *


# 自定义管理器
class BookManage(models.Manager):
	def get_books_by_type(self, type_id, limit=None, sort='default'):
		# 根据商品类型id查询商品信息
		if sort == 'new':  # 按照商品创建时间进行排序
			order_by = ('-create_at',)
		elif sort == 'hot':  # 按照商品销量进行排序
			order_by = ('-sales',)
		elif sort == 'price':  # 按照价格进行排序
			order_by = ('price',)
		else:  # 默认按照主键进行降序排序
			order_by = ('-pk',)

		# 查询数据
		books_li = self.filter(type_id=type_id).order_by(*order_by)  # *不定长参数

		# 查询结果集的限制
		if limit:
			books_li = books_li[:limit]
		return books_li

	# 根据商品id获取商品信息
	def get_books_by_id(self, books_id):
		try:
			books = self.get(id=books_id)
		except self.model.DoesNotExist:
			books = None  # 商品不存在
		return books


# Create your models here.
class Book(BaseModels):
	books_type_choices = ((k, v) for k, v in BOOKS_TYPE.items())
	status_choices = ((k, v) for k, v in STATUS_CHOICE.items())
	type_id = models.SmallIntegerField(default=PYTHON, choices=books_type_choices, verbose_name='商品种类')
	name = models.CharField(max_length=20, verbose_name='商品名称')
	desc = models.CharField(max_length=128, verbose_name='商品描述')
	price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='商品价格')
	unit = models.CharField(max_length=20, verbose_name='商品单位')
	stock = models.IntegerField(default=1, verbose_name='商品库存')
	sales = models.IntegerField(verbose_name='商品销量', default=0)
	detail = HTMLField(verbose_name='商品详情')  # HTMLFiled为富文本编辑器导入的方法
	image = models.ImageField(upload_to='books_image', verbose_name='商品图片')
	status = models.SmallIntegerField(default=OFFLINE, choices=status_choices, verbose_name='商品状态')

	# 实例化自定义管理器
	objects = BookManage()

	class Meta:
		db_table = 's_books'
		verbose_name = '书籍信息'
		verbose_name_plural = verbose_name


	def __str__(self):
		return self.name