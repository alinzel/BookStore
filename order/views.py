from alipay import AliPay
from django.shortcuts import render, redirect
from utils.decorators import login_requier
from django.core.urlresolvers import reverse
from users.models import Address
from books.models import Book
from order.models import OrderInfo, OrderBooks
from books.enums import *
from django_redis import get_redis_connection
from django.http import JsonResponse
from django.db import transaction
from datetime import datetime
import os
import time
from django.conf import settings

# Create your views here.

# 显示提交订单页面

@login_requier
def order_place(request):
	# 接收数据
	books_ids = request.POST.getlist('books_ids')
	print(books_ids)

	# # 校验数据
	if not all(books_ids):
		return redirect(reverse('cart:show'))

	# 用户收货地址
	passport_id = request.session.get('passport_id')
	addr =Address.objects.get_defaut_address(passport_id)

	# 用户要购买的商品信息
	books_li = []
	# 商品总数目和总金额
	total_count = 0
	total_price = 0

	coon = get_redis_connection('default')
	cart_key = 'cart_%d' % passport_id

	for id in books_ids:
		# 根据id获取商品信息
		books = Book.objects.get_books_by_id(id)

		# 从redis中获取用户要买的商品数目
		count = coon.hget(cart_key, id)
		books.count = count
		# 计算商品的小计
		amount = int(count) * books.price
		books.amount = amount
		books_li.append(books)

		#  累计计算商品的总数目和总金额
		total_count += int(count)
		total_price += books.amount

	# 商品的运费和实付款
	transit_price = 10
	total_pay = total_price + transit_price

	# '1,2,3,4'
	books_ids = ','.join(books_ids) #TODO 得到以,分割的字符串
	print(books_ids)

	# 定义上下文环境
	context = {
		'addr' : addr,
		'books_li' : books_li,
		'total_count' : total_count,
		'total_price' : transit_price,
		'transite_price' : transit_price,
		'total_pay' : total_pay,
		'books_ids' : books_ids,
	}

	# 渲染页面
	return render(request, 'order/place_order.html', context)


# 订单提交功能
# 提交订单，需要向两张表中添加信息
# s_order_info:订单信息表 添加一条
# s_order_books: 订单商品表， 订单中买了几件商品，添加几条记录
# 前端需要提交过来的数据: 地址 支付方式 购买的商品id

# 1.向订单表中添加一条信息
# 2.遍历向订单商品表中添加信息
    # 2.1 添加订单商品信息之后，增加商品销量，减少库存
    # 2.2 累计计算订单商品的总数目和总金额
# 3.更新订单商品的总数目和总金额
# 4.清除购物车对应信息

# 事务:原子性:一组sql操作，要么都成功，要么都失败。
# 开启事务: begin;
# 事务回滚: rollback;
# 事务提交: commit;
# 设置保存点: savepoint 保存点;
# 回滚到保存点: rollback to 保存点;
def order_commit(request):
	# 验证用户是否登录
	# 验证用户是否登录
	if not request.session.has_key('islogin'):
		return JsonResponse({'res': 0, 'errmsg': '用户未登录'})

	# 接收数据
	addr_id = request.POST.get('addr_id')
	pay_method = request.POST.get('pay_method')
	books_ids = request.POST.get('books_ids')
	print(books_ids)

	# 进行数据校验
	if not all([addr_id, pay_method, books_ids]):
		return JsonResponse({'res': 1, 'errmsg': '数据不完整'})

	try:
		addr = Address.objects.get(id=addr_id)
	except Exception as e:
		# 地址信息出错
		return JsonResponse({'res': 2, 'errmsg': '地址信息错误'})

	if int(pay_method) not in PAY_METHOD_ENUM.values():
		return JsonResponse({'res': 3, 'errmsg': '不支持的支付方式'})

	# 订单创建
	# 组织订单信息
	passport_id = request.session.get('passport_id')

	# 订单id: 20171029110830+用户的id
	order_id = datetime.now().strftime('%Y%m%d%H%M%S') + str(passport_id)
	print(order_id)
	# 运费
	transit_price = 10
	# 订单商品总数和总金额
	total_count = 0
	total_price = 0

	# 创建一个保存点
	sid = transaction.savepoint()
	try:
		# 向订单信息表中添加一条记录
		order = OrderInfo.objects.create(order_id=order_id,
										 passport_id=passport_id,
										 addr_id=addr_id,
										 total_count=total_count,
										 total_price=total_price,
										 transit_price=transit_price,
										 pay_method=pay_method)
		print('添加订单信息表成功')

		# 向订单商品表中添加订单商品的记录
		books_ids = books_ids.split(',')
		conn = get_redis_connection('default')
		cart_key = 'cart_%d' % passport_id

		# 遍历获取用户购买的商品信息
		for id in books_ids:
			books = Book.objects.get_books_by_id(id)
			if books is None:
				transaction.savepoint_rollback(sid)
				return JsonResponse({'res': 4, 'errmsg': '商品信息错误'})

			# 获取用户购买的商品数目
			count = conn.hget(cart_key, id)
			print(count)

			# 判断商品的库存
			if int(count) > books.stock:
				print('库存不足')
				transaction.savepoint_rollback(sid)
				return JsonResponse({'res': 5, 'errmsg': '商品库存不足'})
			print('111')

			# 创建一条订单商品记录
			OrderBooks.objects.create(order_id=order_id,
									  book_id=id,
									  count=count,
									  price=books.price)
			print('添加商品信息表')

			# 增加商品的销量，减少商品库存
			books.sales += int(count)
			books.stock -= int(count)
			books.save()

			# 累计计算商品的总数目和总额
			total_count += int(count)
			total_price += int(count) * books.price

		# 更新订单的商品总数目和总金额
		order.total_count = total_count
		order.total_price = total_price
		order.save()
	except Exception as e:
		# 操作数据库出错，进行回滚操作
		print(e)
		transaction.savepoint_rollback(sid)
		return JsonResponse({'res': 7, 'errmsg': '服务器错误'})

	# 清除购物车对应记录
	conn.hdel(cart_key, *books_ids)

	# 事务提交
	transaction.savepoint_commit(sid)
	# 返回应答
	return JsonResponse({'res': 6})


# 订单支付的逻辑
def order_pay(request):
	# 用户登录判断
	if not request.session.has_key('islogin'):
		return JsonResponse({
			'res':0,
			'errmsg':'用户未登录'
		})

	# 接收订单id
	order_id = request.POST.get('order_id')

	# 数据校验
	if not order_id:
		return JsonResponse({
			'res':1,
			'errmsg':'订单不存在'
		})
	try:
		order = OrderInfo.objects.get(order_id=order_id,
									  status=1,
									  pay_method=3
									  )
		print('查询成功')
	except OrderInfo.DoesNotExist:
		return JsonResponse({
			'res':2,
			'errmsg':'订单信息出错'
		})

	# 和支付宝进行交付
	alipay = AliPay(
		appid="2016090800464054",  # 应用id
		app_notify_url=None,  # 默认回调url
		app_private_key_path=os.path.join(settings.BASE_DIR, 'order/app_private_key.pem'),
		alipay_public_key_path=os.path.join(settings.BASE_DIR, 'order/alipay_public_key.pem'),
		# 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
		sign_type="RSA2",  # RSA 或者 RSA2
		debug=True,  # 默认False
	)
	print(alipay)

	# 电脑网站支付,需要跳转到https://openapi.alipaydev.com/gateway.do? + order_string
	total_pay = order.total_price + order.transit_price  # decimal
	print(total_pay)
	try:
		order_string = alipay.api_alipay_trade_page_pay(
			out_trade_no=order_id, # 订单id
			total_amount=str(total_pay),
			subject='尚硅谷书城%s' % order_id,
			return_url=None,
			notify_url=None  # 可选, 不填则使用默认notify ur
		)
	except Exception as e:
		print('e: ', e)
	print(order_string)
	# 返回应答
	pay_url = settings.ALIPAY_URL + '?' + order_string
	print(pay_url)

	return JsonResponse({
		'res': 3,
		'pay_url': pay_url,
		'message': 'OK'
	})


# 获取用户支付结果
def check_pay(request):
	# 用户登录判断
	if not request.session.has_key('islogin'):
		return JsonResponse({
			'res':0,
			'errmsg':'用户未登录'
		})

	passport_id = request.session.get('passport_id')
	# 接收订单id
	order_id = request.POST.get('order_id')

	# 数据校验
	if not order_id:
		return JsonResponse({
			'res':1,
			'errmsg':'订单不存在'
		})

	try:
		order = OrderInfo.objects.get(order_id=order_id,
									  passport_id=passport_id,
									  pay_method=3
									  )
	except OrderInfo.DoesNotExist:
		return JsonResponse({
			'res':2,
			'errmsg': '订单信息出错'
		})

	# 和支付宝进行交互

	alipay = AliPay(
		appid="2016090800464054",  # 应用id
		app_notify_url=None,  # 默认回调url
		app_private_key_path=os.path.join(settings.BASE_DIR, 'df_order/app_private_key.pem'),
		alipay_public_key_path=os.path.join(settings.BASE_DIR, 'df_order/alipay_public_key.pem'),
		# 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
		sign_type="RSA2",  # RSA 或者 RSA2
		debug=True,  # 默认False
	)

	while True:
		# 进行支付结果查询
		result = alipay.api_alipay_trade_query(order_id)
		code = result.get('code')
		if code == '10000' and result.get('trade_status')  == 'TRADE_SUCCESS':
			# 用户支付成功
			# 改变订单支付状态
			order.status = 2
			# 填写支付宝交易号
			order.trade_id = result.get('trade_no')
			order.save()
			# 返回数据
			return JsonResponse({
				'res': 3,
				'message':'支付成功'
			})
		elif code =='40004' or (code=='10000' and result.get('trade_status') == 'WAIT_BUYER_PAY'):
			# 支付订单还未完成,继续查询
			# 用户还未完成支付,继续查询
			time.sleep(5)
			continue
		else:
			# 支付出错
			return JsonResponse({
				'res':4,
				'errmsg':'支付出错'
			})














