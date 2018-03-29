from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from books.models import Book
from books.enums import *
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_page
from django_redis import get_redis_connection

# Create your views here.
# 显示首页
# @cache_page(60*3)
def index(request):
	# 查询每个种类的3个新的商品信息和四个销量做好的商品信息
	python_new = Book.objects.get_books_by_type(PYTHON, 3, sort='new')
	python_hot = Book.objects.get_books_by_type(PYTHON, 4, sort='hot')

	javascript_new = Book.objects.get_books_by_type(JAVASCRIPT, 3, sort='new')
	javascript_hot = Book.objects.get_books_by_type(JAVASCRIPT, 4, sort='hot')

	algorithms_new = Book.objects.get_books_by_type(ALGORITHMS, 3, sort='new')
	algorithms_hot = Book.objects.get_books_by_type(ALGORITHMS, 4, sort='hot')

	machinelearning_new = Book.objects.get_books_by_type(MACHINELEARNING, 3, sort='new')
	machinelearning_hot = Book.objects.get_books_by_type(MACHINELEARNING, 4, sort='hot')

	operatingsystem_new = Book.objects.get_books_by_type(OPERATINGSYSTEM, 3, sort='new')
	operatingsystem_hot = Book.objects.get_books_by_type(OPERATINGSYSTEM, 4, sort='hot')

	database_new = Book.objects.get_books_by_type(DATABASE, 3, sort='new')
	database_hot = Book.objects.get_books_by_type(DATABASE, 4, sort='hot')

	# 定义上下文模板
	context = {
		'python_new': python_new,
		'python_hot': python_hot,
		'javascript_new': javascript_new,
		'javascript_hot': javascript_hot,
		'algorithms_new': algorithms_new,
		'algorithms_hot': algorithms_hot,
		'machinelearning_new': machinelearning_new,
		'machinelearning_hot': machinelearning_hot,
		'operatingsystem_new': operatingsystem_new,
		'operatingsystem_hot': operatingsystem_hot,
		'database_new': database_new,
		'database_hot': database_hot,
	}

	# 渲染主页
	return render(request, 'books/index.html', context)


# 商品详情业务逻辑
def detail(request,books_id=None):
	# 获取商品的详情信息--TODO 根据前段传来的书籍id来查找
	books = Book.objects.get_books_by_id(books_id)

	# 如果商品不存在-重定向至首页
	if books == None:
		return redirect(reverse('books:index'))

	# 新品推荐--根据商品类型显示销售量最高的两个商品
	books_li = Book.objects.get_books_by_type(books.type_id, 2, 'new')

	# TODO 登录的用户，每点击一个detail会写入redis
	# 判断用户是否登录,登陆后浏览才有记录,TODO 存储格式history_用户id':[10,9,2,3,4]
	if request.session.has_key('islogin'):
		# 用户已经登录,记录浏览记录
		coon = get_redis_connection('default')
		key = 'history_%d' % request.session.get('passport_id')

		# 先从redis中去除books.id-->TODO 去除重复的书ID
		coon.lrem(key,0,books.id)
		# 以列表形式存储key,value -->用户id 书的ID
		coon.lpush(key,books.id)
		# 保存用户最近浏览的5个商品
		coon.ltrim(key,0,4) # 切片操作

	# 定义上下文环境
	context = {'books': books, 'books_li': books_li}

	# 渲染商品细节的页面
	return render(request, 'books/detail.html', context)
	# return render(request, 'books/detail.html')


# 列表页的逻辑
# 商品种类 页码 排序方式
# /list/(种类id)/(页码)/?sort=排序方式
def list(request, type_id, page):
	# 获取排序方式
	sort = request.GET.get('sort', 'default')

	# 判断type_id是否合法
	if int(type_id) not in BOOKS_TYPE.keys():
		return redirect(reverse('books:index'))

	# 根据商品种类id和排序方式查询数据,得到所有符合条件的列表集合
	books_list = Book.objects.get_books_by_type(type_id=type_id, sort=sort)

	# 分页-->实例化Paginator(要显示的内容集合,每页显示几个)
	paginator = Paginator(books_list, 1)

	# 获取分页后的总数据-->实例化的paginator对象.num_pages
	num_pages = paginator.num_pages

	# 对参数进行判断:如果参数page 为空,或者大于总页数,将pagef赋值为1
	if page == '' or int(page) > num_pages:
		page = 1
	else:  # 将参数page转化为整数
		page = int(page)

	# 得到page页对象
	books_li = paginator.page(page)  # page为处理过的page

	# 对页码进行控制
	# 1.总页数<5, 显示所有页码
	# 2.当前页是前3页，显示1-5页
	# 3.当前页是后3页，显示后5页 10 9 8 7
	# 4.其他情况，显示当前页前2页，后2页，当前页
	if num_pages < 5:
		pages = range(1, num_pages+1)  # 得到列表形式[1,...num_pages]
	elif page <= 3:
		pages = range(1,6)
	elif num_pages - page <= 2:
		pages = range(num_pages - 4, num_pages + 1)
	else:
		pages = range(page-2, page+3)

	# 新品推荐
	books_new = Book.objects.get_books_by_type(type_id, limit=2, sort='new')

	# 定义上下文环境
	type_title = BOOKS_TYPE[int(type_id)]  # 根据key得出value(书名)
	context = {
		'books_li' : books_li,  # 当前页对象,列表
		'books_new' : books_new,  # 新书
		'type_id' : type_id,  # 书籍类型
		'sort' : sort,  # 排序类型
		'type_title' : type_title,
		'pages' : pages,   # 页数显示
	}

	# 渲染页面
	return render(request, 'books/list.html', context)






