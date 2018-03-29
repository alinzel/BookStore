from django.shortcuts import render,redirect
from django.http import JsonResponse, HttpResponse
from django.core.urlresolvers import reverse
from users.models import PassPort, Address
from books.models import Book
from order.models import OrderBooks, OrderInfo
import re
from utils.decorators import login_requier
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from django.conf import settings
from django.core.mail import send_mail
from users.tasks import send_active_email
from django_redis import get_redis_connection

# Create your views here.
def register(request):
	return render(request, 'users/register.html')

# 注册试图
def register_handle(request):
	# 获取表单提交信息

	username = request.POST.get('user_name')
	password = request.POST.get('pwd')
	email = request.POST.get('email')

	# 对用户名进行校验
	if not username:  # 判空
		return render(request, 'users/register.html', {'username_error': '用户名不能为空'})
	elif not re.match(r'^\w{5,20}$',username):  # 判格式
		return render(request, 'users/register.html', {'username_error': '确认用户名长度在5-20间'})

	# 对密码进行校验
	if not password:
		return render(request, 'users/register.html', {'pwd_error': '密码不能为空'})
	elif not re.match(r'^\w{8,20}$',password):
		return render(request, 'users/register.html', {'pwd_error': '确认密码在8-20间'})

	if not email:
		return render(request, 'users/register.html', {'email_error': '邮箱不能为空'})
	elif not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
		return render(request, 'users/register.html', {'email_error': '邮箱格式不对'})
	# 固定传参的方式
	# PassPort.objects.add_one_passport(username=username, password=password, email=email)
	# 普通传参的方式
	passport = PassPort.objects.add_one_passport(username, password, email)

	# Serializer-->序列化器,将settings.SECRET_KEY序列化为字典形式,并设置过期时间3600秒
	serializer = Serializer(settings.SECRET_KEY, 3600)
	# 反序列化-得到字节形式-->TODO 序列化并签名一个用户ID
	token = serializer.dumps({'confirm': passport.id})  # 返回bytes
	# 因为是字节形似所以要解码
	token = token.decode()

	# TODO 同步发送邮件
	# # 给用户的邮箱发激活邮件
	# send_mail('尚硅谷书城用户激活', '', settings.EMAIL_FROM, [email],
	# 		  html_message='<a href="http://127.0.0.1:8000/user/active/%s/">http://127.0.0.1:8000/user/active/</a>' % token)

	# TODO 异步发送邮件
	# 调用celery中的任务,并传参
	send_active_email.delay(token,username,email)

	# return HttpResponse('注册成功')
	return redirect(reverse('books:index'))


# 定义登录页面
def login(request):
	# TODO 回显--从cooki中读取数据,并显示在前端的输入框'
	username = request.COOKIES.get('username', '')
	password = request.COOKIES.get('password', '')

	context = {
		'username': username,
		'password' : password,
	}
	return render(request, 'users/login.html',context)


'''用户登录验证功能--当ajax请求的时候通过路由找到此函数'''
def login_check(request):
	# TODO 获取用户提交的数据--get(参数)-参数为ajax传过来的参数,而不是name属性
	username = request.POST.get('username')
	password = request.POST.get('password')
	remember = request.POST.get('remember')
	verifycode = request.POST.get('verifycode')

	# 提交判空校验--返回json格式的数据给前段使用
	if not all([username, password, verifycode]):
		return JsonResponse({
			'res': 2,
		})

	# 调用自定义的方法,如果与数据库匹配正确,返回用户名和密码
	passport = PassPort.objects.get_one_passport(username, password)

	# 验证用户是否激活
	if passport.is_active:
		# 用户名密码正确
		if passport:
			# 从session中获取数据,并重定向至首页
			# TODO 获取字典方式的用法--当session中有'url_path'这个字段,会将'url_path'的值赋值给next_url
			# TODO 当session中没有'url_path'这个字段,会将重定向的的反向解析地址赋值给next_url
			next_url = request.session.get('url_path', reverse('books:index'))

			jres = JsonResponse({
				'res':1,
				'next_url':next_url
			})

			# 判断验证码--TODO 前台获取到的用户输入验证码与生成验证码时存在session中的对比
			if verifycode != request.session.get('verifycode','error'):
				return JsonResponse({
					'res':3,
					'errmsg':'验证码错误'
				})


			# 判断是否记住用户名
			if remember == 'true':
				# 记住用户名写入cooki
				jres.set_cookie('username',username, max_age=7*24*3600)
				jres.set_cookie('password', password, max_age=7 * 24 * 3600)

			else:
				# 不记住删除cooki
				jres.delete_cookie('username')

			# 记录用户登录状态--写入session
			request.session['islogin'] = True
			request.session['username'] = username
			request.session['passport_id'] = passport.id
			return jres
		# 用户名密码错误
		else:
			return JsonResponse({
				'res':0
			})
	else:
		return JsonResponse({
			'res': 4,
			'errmsg':'该账户未激活'
		})


# 注销功能
def logout(request):
	# 清空用户的session信息
	request.session.flush()
	# 退出后重定向到首页
	return redirect(reverse('books:index'))


@login_requier  # 验证是否登录的装饰器--只有登陆后才能使用用户中心
# 定义用户中心功能逻辑
def user(request):
	# TODO 从session中获取passport_id
	passport_id = request.session.get('passport_id')

	# 获取用户信息
	addr = Address.objects.get_defaut_address(passport_id)

	# 连接redis
	coon = get_redis_connection('default')
	key = 'history_%d' % passport_id

	# 取出用户最近浏览的5个商品ID
	history_li = coon.lrange(key, 0, 4)

	# 初始化一个列表,存放所有书籍对象
	books_li =[]

	# 遍历浏览记录中书的ID,并拿到对应书的对象
	for id in history_li:
		books = Book.objects.get_books_by_id(id)
		books_li.append(books)

	context = {
		'addr': addr,
		'page': 'user',
		'book_li': books_li,
	}

	# 渲染页面
	return render(request, 'users/user_center_info.html', context)


# 订单详情页的渲染
@login_requier
def order(request):
	# 查询用户的订单信息
	passport_id = request.session.get('passport_id')

	# 获取订单信息
	order_li = OrderInfo.objects.filter(passport_id=passport_id)

	# 遍历获取订单的商品信息
	# order->OrderInfo实例对象
	for order in order_li:
		# 根据订单id查询订单商品信息
		order_id = order.order_id
		order_books_li = OrderBooks.objects.filter(order_id=order_id)

		# 计算商品的小计
		# order_books ->OrderBooks实例对象
		for order_books in order_books_li:
			count = order_books.count
			price = order_books.price
			amount = count * price
			# 保存订单中每一个商品的小计
			order_books.amount = amount

		# 给order对象动态增加一个属性order_books_li,保存订单中商品的信息
		order.order_books_li = order_books_li

	context = {
		'order_li': order_li,
		'page': 'order'
	}

	return render(request, 'users/user_center_order.html', context)


# 用户中心地址页的渲染逻辑
@login_requier
def address(request):
	# 获取用户登录的id
	passport_id = request.session.get('passport_id')

	if request.method == 'GET':
		# 显示地址页面
		# 查询用户的默认地址
		addr = Address.objects.get_defaut_address(passport_id)
		print(addr)
		return render(request, 'users/user_center_site.html', {'addr': addr, 'page': 'addre'})
	else:
		# 添加收货地址
		# 接收数据
		recipient_name = request.POST.get('username')
		recipient_addr = request.POST.get('addr')
		zip_code = request.POST.get('zip_code')
		recipient_phone = request.POST.get('phone')

		# 进行校验
		if not all([recipient_name, recipient_addr, zip_code, recipient_phone]):
			return render(request, 'users/user_center_site.html', {'errmsg': '参数不能为空'})

		# 添加收货地址
		Address.objects.add_one_address(passport_id=passport_id,
										recipient_name=recipient_name,
										recipient_addr=recipient_addr,
										zip_code=zip_code,
										recipient_phone=recipient_phone)

		# 返回应答
		return redirect(reverse('user:address'))


# 验证码逻辑
def verifycode(request):
	# 引入绘图模块
	from PIL import Image, ImageDraw, ImageFont
	# 引入随机函数模块
	import random

	# 定义变量,用于画面背景色.宽,高
	bgcolor = (random.randrange(20,100), random.randrange(20,100), 255)
	width = 100
	height = 25
	# 创建画面对象
	im = Image.new('RGB',(width,height),bgcolor)
	# 创建画笔对象
	draw = ImageDraw.Draw(im)
	# 调用画笔的point函数绘制噪点
	for i in range(0,100):
		xy = (random.randrange(0,width), random.randrange(0,height))
		fill = (random.randrange(0,255),255,random.randrange(0,255))
		draw.point(xy,fill=fill)
	# 定义验证码的备选值
	str1 = 'ABCD123EFGHIJK456LMNOPQRS789TUVWXYZ0'
	# 初始化验证码
	rand_str = ''
	# 随机选取4个值作为验证码
	for i in range(4):
		rand_str += str1[random.randrange(0,len(str1))]
	# 构造字体对象
	font = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMono.ttf', 25)
	# 构造字体颜色
	fontcolor = (255, random.randrange(0,255), random.randrange(0,255))
	# 绘制4个字
	# TODO 显示位置,第一位验证码,字体,字体颜色
	draw.text((5,2),rand_str[0],font=font,fill=fontcolor)
	draw.text((25, 2), rand_str[1], font=font, fill=fontcolor)
	draw.text((50, 2), rand_str[2], font=font, fill=fontcolor)
	draw.text((75, 2), rand_str[3], font=font, fill=fontcolor)
	# 释放画笔
	del draw
	# 存入session,用于做进一步验证,TODO 用于比对与用户输入的是否一致
	request.session['verifycode'] = rand_str
	# 内存文件操作
	import io
	# 实例化内存,
	buf = io.BytesIO()
	# 将图片保存在内存中,文件类型为png
	im.save(buf, 'png')
	# 将内存中的图片显示给客户端,MIME类型为图片png
	return HttpResponse(buf.getvalue(), 'image/png')


# 用户账户激活
def register_active(request, token):
	# 将setting配置文件里的秘钥序列化成一个URL编码的字符串,并设置过期时间
	serializer = Serializer(settings.SECRET_KEY, 3600)
	try:
		# TODO loads(JSON字符串)-->JSON对象    dumps(JSON对象)-->JSON字符串
		info = serializer.loads(token)
		# TODO 得到注册链接中的passport_id (注册时候序列化为token字符串传过来了)
		passport_id = info['confirm']
		# 进行用户激活
		passport = PassPort.objects.get(id=passport_id)
		# 将数据库的is_active的字段设置为true
		passport.is_active = True
		passport.save()
		# 点击激活链接--> 跳转到登录页面
		return redirect(reverse('user:login'))
	# 激活链接已经过期的错误,点击链接时候显示链接已过期
	except SignatureExpired:
		# 链接过期
		return HttpResponse('激活链接已过期')



