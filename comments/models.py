from django.db import models
from db.Base_DB import BaseModels
from users.models import PassPort
from books.models import Book

# Create your models here.

# 定义评论表
class Comments(BaseModels):
	disabled = models.BooleanField(default=False, verbose_name='禁用评论')
	# TODO 外建的引用,应用.模型
	user = models.ForeignKey('users.PassPort', verbose_name='用户ID')
	book = models.ForeignKey('books.Book', verbose_name='书籍ID')
	content = models.CharField(max_length=1000, verbose_name='评论内容')

	class Meta:
		db_table = 's_comment_table'

