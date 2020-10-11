def ignore(func, ret=None):
	try:
		return func()
	except Exception as e:
		if ret == '__exception__':
			return e
		else:
			return ret