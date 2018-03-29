from django.shortcuts import render,redirect
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from comments.models import Comments
from books.models import Book
from users.models import PassPort
from django.views.decorators.csrf import csrf_exempt
import json
import redis

# Create your views here.

# 设置过期时间
EXPIRE_TIME = 60 *5
# 连接redis数据库 TODO ?嘛意思
pool = redis.ConnectionPool(host='localhost', port=6379, db=2)
redis_db = redis.Redis(connection_pool=pool)

@csrf_exempt # TODO 解决表单的安全校验
@require_http_methods(['GET','POST']) # TODO 此装饰器的作用-->使视图函数只接受固定的请求方式
def comment(request, books_id):
	book_id = books_id  # books_id路径中的参数
	# 如果是get请求
	if request.method =='GET':
		# 现在redis里面寻找评论(有过期时间所以可能查不到)
		# TODO 存储的key comment_4(书的ID),值为字符串
		c = redis_db.get('comment_%s' % book_id)
		try :
			# 将查找的评论内容解码
			c = c.decode('utf-8')
		except:
			pass
		# 如果查找到评论内容 TODO c = {'comment_4':'评论内容','comment_4':'评论内容'}
		if c:
			# 返回json数据
			return JsonResponse({
				'code':200,
				'data':json.loads(c) # TODO json反序列化,字符串形式转化为字典形式
			})
		else:
			# 找不到,就从数据库里面取 TODO 得到queryset集合(所有评论的集合)
			# TODO [<Comments: Comments object>, <Comments: Comments object>,
			comments = Comments.objects.filter(book_id=book_id)
			print(comments)
			# 初始化一个空列表
			data =  []
			# 遍历得到的评论集合，TODO 得到每一个用户的一条评论
			for c in comments:
				# 通过评论实例对象得到用户ID与评论内容,并添加到一个空列表中
				data.append({
					'user_id':c.user_id,
					'content': c.content
				})

			res = {
				'code': 200,
				'data': data
			}
			try:
				# TODO json.dump-->得到json字符串
				# 将评论内容写到redis数据库中,并设置过期时间
				redis_db.setex('comment_%s' % book_id, json.dumps(data), EXPIRE_TIME)
			except Exception as e:
				print('e:',e)

			return JsonResponse(res)
	# 如果请求方式不是GET
	else:
		# 从页面POST请求得到数据并解码
		# TODO {'user_id': 11, 'book_id': 4, 'content': 'params'}
		params = json.loads(request.body.decode('utf-8'))

		# 分别取出用户id,书籍ID,评论内容
		book_id = params.get('book_id')
		user_id = params.get('user_id')
		content = params.get('content')

		# 通过用户ID和书籍ID得到书籍与用户对象
		book = Book.objects.get(id=book_id)
		user = PassPort.objects.get(id=user_id)

		# 往数据库里插入一条评论信息的数据,并保存
		comment = Comments(book=book, user=user, content=content)
		comment.save()

		# 返回的内容
		return JsonResponse({
			'code':200,
			'msg':'评论成功',
		})






		

















