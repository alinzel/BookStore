# 自定义模板过滤器
from django.template import Library

# 创建一个Library对象 TODO 必须是register 才能是过滤器是可用的标签库函数
register = Library()

# 创建一个过滤器函数,返回订单状态对应的字符串
@register.filter
# TODO 自定义的过滤器函数，参数为页面的值
def order_status(status):
	status_dict = {
		# 参数的实际值：要显示的内容
		0:'已付款',
		1:'待支付',
		2: "待发货",
		3: "待收货",
		4: "待评价",
		5: "已完成",
	}
	# 返回形式：字典名称【参数】
	return status_dict[status]