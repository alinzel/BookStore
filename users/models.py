from django.db import models
from db.Base_DB import BaseModels
from utils.get_hash import get_hash
# Create your models here.


# 自定义管理器
class PassportManage(models.Manager):
	# 自定义一个方法：用来获取数据库数据
	def get_one_passport(self, username, password):
		try:
			passport = self.get(username=username, password=get_hash(password))
		except self.model.DoesNotExist:  # 指定异常捕获
			# 账户不存在-->self.model-->model当前查询的模型，
			passport = None
		# except Exception as e:
		# 	# 只要抛出异常就被捕获
		# 	print(e)
		return passport

	# 自定义一个方法：用来向数据库添加数据
	def add_one_passport(self, username, password, email):
		try:
			passport = self.create(username=username, password=get_hash(password), email=email)
		except self.model.DoesNotExist:  # 指定异常捕获
			# 账户不存在-->self.model-->model当前查询的模型，
			passport = None
		return passport


# 自定义地址模型的管理器
class AddressManage(models.Manager):
	# 查询指定用户的默认收货地址
	def get_defaut_address(self, passport_id):
		try:
			addr = self.get(passport_id=passport_id, is_default=True)
		except self.model.DoesNotExist:
			addr = None
		return addr

	# 添加收货地址
	def add_one_address(self,passport_id,  recipient_name, recipient_addr, zip_code, recipient_phone):
		addr = self.get_defaut_address(passport_id)

		# 判断获取到的收货地址的是不是默认地址
		if  addr:
			# 存在默认地址
			is_default = False
		else:
			# 不存在默认地址
			is_default = True

		# 添加一个新地址
		addr = self.create(passport_id=passport_id,
						   recipient_name=recipient_name,
						   recipient_addr=recipient_addr,
						   zip_code=zip_code,
						   recipient_phone=recipient_phone,
						   is_default=is_default
						   )

		return addr


# 创建一个用户表
class PassPort(BaseModels):
	username = models.CharField(verbose_name='用户名', max_length=20)
	password = models.CharField(verbose_name='密码', max_length=40)
	email = models.EmailField(verbose_name='邮箱')
	is_active = models.BooleanField(verbose_name='激活状态', default=False)

	class Meta:
		db_table = 's_user_account'

	def __str__(self):
		return self.username

	# 在某个模型中实例化自定义的管理器
	objects = PassportManage()

# 创建一个地址表
class Address(BaseModels):
	recipient_name = models.CharField(max_length=20, verbose_name='收件人姓名')
	recipient_addr = models.CharField(max_length=256, verbose_name='收件人地址')
	zip_code = models.CharField(max_length=6, verbose_name='邮政编码')
	recipient_phone = models.CharField(max_length=11, verbose_name='联系电话')
	is_default = models.BooleanField(default=False, verbose_name='是否默认')
	passport = models.ForeignKey('PassPort', verbose_name='账户')

	objects = AddressManage()

	class Meta:
		db_table = 's_user_address'

	def __str__(self):
		return self.recipient_name