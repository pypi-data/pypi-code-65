import random
print(':testing:', random.random())

def on_request(request):
	print(':testing (request):', request)