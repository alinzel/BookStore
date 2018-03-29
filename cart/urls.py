from django.conf.urls import url
from cart import views

urlpatterns = [
	# 购物车页面的路由
	url(r'^show', views.cart_show, name='show'),
	# 像购物车添加商品的路由
	url(r'^add/$', views.cart_add, name='add'),
	# 获取购物车数量的路由
	url(r'^count/$', views.cart_count, name='count'),
	# 删除商品的路由
	url(r'^del', views.car_del, name='del'),
	# 更新商品的路由
	url(r'^update', views.cart_update, name='update'),
]