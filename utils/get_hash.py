from hashlib import sha1


# 定义一个加密函数，给密码进行加密
def get_hash(password):
	# 获取字符串进行加密
	sh = sha1()
	sh.update(password.encode('utf-8'))
	return sh.hexdigest()