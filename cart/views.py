from django.shortcuts import render
from django.http import JsonResponse
from books.models import Book
from utils.decorators import login_requier
from django_redis import get_redis_connection

# Create your views here.


# 向购物车中添加商品功能逻辑
def cart_add(request):
	# 判断用户是否处于登录状态
	if not request.session.has_key('islogin'):
		return JsonResponse({
			'res' : 0,
			'errmsg': '请先登录'
		})

	# 获取前端传过来的数据--ajax获取
	book_id = request.POST.get('books_id')  # 具体哪一本书
	books_count = request.POST.get('books_count')  # 书的总数

	# 进行数据校验--如果获取的数据为空,返回相应信息
	if not all([book_id, books_count]):
		return JsonResponse({
			'res' : 1,
			'errmsg' : '数据不完整'
		})

	# 通过输的id获取到书的实例对象
	books = Book.objects.get_books_by_id(book_id)
	if books is None:
		return  JsonResponse({
			'res' : 2,
			'errmsg' : '商品不存在'
		})

	# 对商品数量的校验
	try:
		books_count = int(books_count)  # 将获取的数量转换为整形
	except Exception as  e:
		return JsonResponse({
			'res' : 3,
			'errmsg' : '商品数量必须为整数'
		})

	# 添加商品到购物车--添加到redis中
	# 链接redis数据库
	conn = get_redis_connection('default')  # TODO default-->setting的默认设置
	# 拿用户的id-->写入session的id
	cart_key = 'cart_%d' % request.session.get('passport_id')

	# 每个用户的购物车记录用一条哈希数据来保存,格式cart_用户id  商品id 商品数量
	# 根据用户第和商品id TODO 获取购物车中该商品的数量
	res = conn.hget(cart_key, book_id)  # res为购物车中存在的,books_count为从前端获取的数据
	if res is None:
		# 如果购物车没有添加该商品,则添加该数据
		res = books_count
	else:
		# 如果该购物车已经添加过该商品,则累计
		res = int(res) + books_count

	# 判断购物车中商品的库存
	if res > books.stock:
		return JsonResponse({
			'res' : 4,
			'errmsg' : '商品库存不足'
		})
	else:
		# 库存够,通过哈希存入到redis的购物车
		conn.hset(cart_key, book_id,res)
		# 加入购物车,返回结果
		return JsonResponse({
			'res' : 5,
			'errmsg' : '已添加到购物车'
		})


# 登陆后可以看到购物车中的商品数量的逻辑
def cart_count(request):
	# 判断用户是否登录
	if not request.session.has_key('islogin'):
		return JsonResponse({
			'res' : 0,
			'errmsg' : '请先登录,未登录'
		})

	# 计算用户购物车商品的数量
	# 链接redis数据库
	coon = get_redis_connection('default')
	cart_key = 'cart_%d' % request.session.get('passport_id')

	# 计算该用户购物车中的数量,并将结果返回给前端
	res = 0  # 初始化要返回给前端的结果
	# 获取用户购物车里的每个商品数目-->列表形式
	res_list = coon.hvals(cart_key)
	# 遍历获取商品数目,并做累计
	for i in res_list:
		res += int(i)

	# 将累计后的结果返回前端
	return JsonResponse({
		'res' : res
	})


@login_requier
# 显示用户购物车逻辑
def cart_show(request):
	passport_id = request.session.get('passport_id')

	# 获取用户购物车的记录
	conn = get_redis_connection('default')
	cart_key = 'cart_%d' % passport_id
	print(cart_key)
	# 从redis获取购物车数据
	res_dict = conn.hgetall(cart_key) #{'id':count}
	# print(res_dict)

	books_li = []
	# 初始化所有商品的数目
	total_count = 0
	# 初始化所有商品的总价格
	total_price = 0

	# 遍历购物车中所有数据
	for id, count in res_dict.items():
		# print(id)
		# print(count)

		# 通过书的id获取到书的信息
		books = Book.objects.get_books_by_id(id)

		# 保存书的数目-->TODO 实例化的对象动态添加属性,并不是模型的字段??
		books.count = count
		# 保存商品小计
		books.amount = int(count) * books.price
		books_li.append(books)

		total_count += int(count)
		total_price += int(count) * books.price

	# 定义上下文环境
	context = {
		'books_li': books_li,
		'total_count': total_count,
		'total_price': total_price
	}

	# 渲染页面
	return render(request, 'cart/cart.html', context)


# 购物车中删除商品的功能
def car_del(request):
	print('1111')
	# 判断用户是否登录
	if not request.session.has_key('islogin'):
		return JsonResponse({
			'res' : 0,
			'errmsg' : '请先登录'
		})

	# 接收ajax传过来的数据
	books_id = request.POST.get('books_id')

	# 校验商品是否存放
	if not all([books_id]):
		return JsonResponse({
			'res':1,
			'errmsg':'数据不完整'
		})

	books = Book.objects.get_books_by_id(books_id)
	if books is None:
		return JsonResponse({
			'res' : 2,
			'errmsg' : '商品不存在'
		})

	# 删除购物车商品信息
	coon = get_redis_connection('default')
	cart_key = 'cart_%d' % request.session.get('passport_id')
	coon.hdel(cart_key, books_id)

	return JsonResponse({
		'res' : 3,
		'errmsg' : '删除成功'
	})


# 购物车页面编辑商品数量
def cart_update(request):
	# 判断用户是否登录
	if not request.session.has_key('islogin'):
		return JsonResponse({
			'res' : 0,
			'errmsg' : '请先登录'
		})

	# 接收数据
	books_id = request.POST.get('books_id')
	books_count = request.POST.get('books_count')

	# 数据的校验
	if not all([books_id, books_count]):
		return JsonResponse({
			'res':1,
			'errmsg': '数据不完整'
		})

	# 通过id获取书籍信息
	books = Book.objects.get_books_by_id(books_id)
	if books is None:
		return JsonResponse({
			'res' : 2,
			'errmsg' : '商品不存在'
		})

	try:
		books_count = int(books_count)
	except Exception as e:
		return JsonResponse({
			'res' : 3,
			'errmsg' : '商品数量必须为数字'
		})

	# 链接redis并获取当前用户购物车状态
	coon = get_redis_connection('default')
	cart_key = 'cart_%d' % request.session.get('passport_id')

	# 判断商品库存
	if books_count > books.stock:
		return JsonResponse({
			'res' : 4,
			'errmsg' : '商品库存不足'
		})

	coon.hset(cart_key, books_id, books_count)
	return JsonResponse({
		'res' : 5,
		'errmsg' : '更新成功'
	})

