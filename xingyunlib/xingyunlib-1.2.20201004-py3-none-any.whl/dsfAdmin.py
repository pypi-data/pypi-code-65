def get_interpreter():
	import sys
	return sys.executable

def get_pakages():
	import os
	import re
	# http://127.0.0.1:55820/package/search?name=xingyunlib
	interpreter_pos = get_interpreter()
	# print(os.getcwd())
	z = os.popen(interpreter_pos + " -m pip list")
	a = z.read()
	z.close()
	c = a.split("\n")[2:]
	num = []
	for x in c:
		x = re.split("\s", x)
		while "" in x:
			x.remove("")
		if x == []:
			continue
		num.append(x)
	return num


def find_pakages(pakage, ver=False):
	Ls = get_pakages()
	for x in Ls:
		if x[0] == pakage:
			if ver:
				if x[1] == ver:
					return True
				else:
					return x[1]
			return True
	return False


def upgrade_pakages(pakage):
	import os
	if type(pakage) != type(" "):
		pakage = "".join(pakage)
	os.system(get_interpreter() + " -m pip install --upgrade " + pakage)


def install_pakages(pakage, interpreter=None):
	import os
	if type(pakage) != type(" "):
		pakage = " ".join(pakage)
	if interpreter == None:
		interpreter = get_interpreter()
	print(pakage)
	os.system(interpreter + " -m pip install " + pakage + " -i https://pypi.douban.com/simple")


def dump_pip_list(filename):
	with open(filename + ".pip", "w", encoding="utf-8")as f:
		f.write(str(get_pakages()))


def load_pip_list(filename, interpreter=None):
	with open(filename + ".pip", "r", encoding="utf-8")as f:
		z = eval(f.read())
		# print(z)
		b = []
		for x in z:
			b.append(x[0])
		install_pakages(b, interpreter=interpreter)

# print(find_packages("xingyunlib"))
# exit()