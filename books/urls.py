from django.conf.urls import url, include
from books import views

urlpatterns = [
	url(r'^index/$', views.index, name='index'),
	# url(r'^detail/$', views.detail, name='detail'),
	url(r'detail/(?P<books_id>\d+)/$', views.detail, name='detail'),
	url(r'^list/(?P<type_id>\d+)/(?P<page>\d+)/$', views.list, name='list')
]