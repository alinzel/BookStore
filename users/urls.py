from django.conf.urls import url
from users import views


urlpatterns = [
    url(r'^register/$',views.register, name='register'),
    url(r'^register_handle/$',views.register_handle, name='register_handle'),
    url(r'^login/$',views.login, name='login'),
    url(r'^login_check/$', views.login_check, name='login_check'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^user/$', views.user, name='user'),
    url(r'^order/$', views.order, name='order'),
    url(r'^address/$', views.address, name='address'),
    # 验证码的路由
    url(r'^verifycode/$', views.verifycode, name='verifycode'),
    # 激活链接 TODO .表示匹配任意一个字符,只匹配一次,* 表示前面字符可以出现0次或者多次
    url(r'^active/(?P<token>.*)/$', views.register_active, name='active'),
]