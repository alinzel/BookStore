from django.db import models
from db.Base_DB import BaseModels
from books.enums import *


# Create your models here.

# 订单信息的模型
class OrderInfo(BaseModels):
	order_id = models.CharField(max_length=64, primary_key=True, verbose_name='订单编号')
	passport = models.ForeignKey('users.PassPort', verbose_name='下单账户')
	addr = models.ForeignKey('users.Address', verbose_name='收货地址')
	total_count = models.IntegerField(default=1, verbose_name='商品总数')
	total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='商品总价')
	transit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='订单运费')
	pay_method = models.SmallIntegerField(choices=PAY_METHOD_CHOICES, default=1, verbose_name='支付方式')
	status =  models.SmallIntegerField(choices=ORDER_ATATE_CHOICES, default=1, verbose_name='订单状态')
	trade_id = models.CharField(max_length=100, unique=True, null=True, blank=True, verbose_name='支付编号')

	class Meta:
		db_table = 's_order_info'


# 订单商品信息的模型
class OrderBooks(BaseModels):
	order = models.ForeignKey('OrderInfo', verbose_name='所属订单')
	book = models.ForeignKey('books.Book', verbose_name='订单商品')
	count = models.IntegerField(default=1, verbose_name='商品数量')
	price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='价格')

	class Meta:
		db_table = 's_order_books'




