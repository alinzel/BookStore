# 用来判断用户是否处于登录状态的逻辑
from django.shortcuts import redirect
from django.core.urlresolvers import reverse


# 判断登录的装饰器-->只有登陆后才能使用用户中心
def login_requier(view_func):
	def wrapper(request, *args,  **kwargs):
		# 如果session中的islogin为True,说明已经登录成功,返回用户视图函数
		if request.session.has_key('islogin'):
			return view_func(request, *args, **kwargs)
		else:  # 否则跳转到登录页
			return redirect(reverse('user:login'))
	return wrapper
