from django.conf.urls import include, url
from order import  views

urlpatterns = [
	# 订单提交页面的路由
	url(r'^place/$', views.order_place, name='place'),
	url(r'^commit/$',views.order_commit, name='commit'),
	# 订单支付路由
	url(r'^pay/$',views.order_pay, name='pay'),
	# 查询支付结果路由
	url(r'^check_pay/$',views.check_pay, name='check_pay'),


]