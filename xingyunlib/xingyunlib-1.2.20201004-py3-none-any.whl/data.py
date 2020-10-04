# from . import err
class Data(object):
	def __init__(self,initfile="",find=False):
		if initfile=="":
			raise FileExistsError("未指定打开的文件")
		try:
			if find==False:
				try:
					a = open(initfile, "r")
					self.data = eval(a.read())
				except:
					a = open(initfile,"w")
					self.data = eval(a.read())
			else:
				a = open(initfile, "r")
				self.data = eval(a.read())
		except:
			raise FileNotFoundError("未能找到要打开的文件")
		self.file=initfile
	def eval_load(self):
		try:
			self.data=eval(self.data)
			return self.data
		except:
			return self.data
	def change_data(self,w):
		self.data=w
	def save(self):
		with open(self.file,"w") as f:
			try:
				f.write(self.data)
			except:
				try:
					f.write(str(self.data))
				except:
					# 翻译的变量：FileExistsError
					# 原始的语句：File Exists Error
					# 中文含义：文件存在错误
					raise IOError("无法保存此数据！")
	def reload(self,initfile="",find=False):
		if initfile=="":
			raise FileExistsError("未指定打开的文件")
		try:
			if find==False:
				try:
					a = open(initfile, "r")
					self.data = eval(a.read())
				except:
					a = open(initfile,"w")
					self.data = eval(a.read())
			else:
				a = open(initfile, "r")
				self.data = eval(a.read())
		except:
			raise FileNotFoundError("未能找到要打开的文件")
		self.file=initfile
class Key:
	def __init__(self,filename=None):
		if filename!=None:
			try:
				with open(filename,"r") as f:
					self.encode=f.read()
			except:
				self.encode = filename
		else:
			self.encode=None
			self.decode=None
	def decoding(self,key,v=2):
		s=list(self.encode)
		for x in range(len(self.encode)):
			for y in list(key):
				if x % v==0:
					s[x] = chr(abs(ord(s[x])-ord(y)))
				else:
					s[x] = chr(abs(ord(s[x]) + ord(y)))
		self.decode="".join(s)
		return s
	def encoding(self,txt,key,v=2):
		s = list(txt)
		for x in range(len(txt)):
			for y in list(key):
				if x % v == 0:
					s[x] = chr(abs(ord(s[x]) + ord(y)))
				else:
					s[x] = chr(abs(ord(s[x]) - ord(y)))
		self.encode = "".join(s)
		self.decode = txt
		return s
	def sava_encode(self,filename):
		with open(filename,"w") as f:
			f.write(self.encode)