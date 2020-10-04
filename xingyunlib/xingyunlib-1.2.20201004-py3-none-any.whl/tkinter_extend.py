# 输入文本框(带按钮，按enter也可以运行)
"""
创建(就当button控件用)：
a=inpu_box(tk,函数名,**按钮的配置)

打包：
a.pack(**pack的配置)

配置：
a.config_entry(**文本框的配置)
a.config_button(**按钮的配置)
其实你基本可以当做Entry来用，除了初始化语句还有配置以外基本都是一样的
"""


class inpt_box:
	def __init__(self, *w, command, **arg):
		import tkinter as tk
		self.Frame = tk.Frame(*w)
		self.cmd = command
		self.Entry = tk.Entry(self.Frame, bd=3)
		self.Button = tk.Button(self.Frame, command=self.cmd, **arg)

	def config_entry(self, **arg):
		self.Entry.configure(**arg)

	def config_button(self, **arg):
		self.button.configure(**arg)

	def get(self):
		return self.Entry.get()

	def insert(self, *w):
		self.Entry.insert(*w)

	def delete(self, *w):
		self.Entry.delete(*w)

	def _kao(self, *event):
		self.cmd()

	def pack(self, **arg):
		self.Entry.pack(fill="x", side="left", expand=True)
		self.Button.pack(fill="x", side="left")
		self.Entry.bind("<Return>", self._kao)
		self.Frame.pack(**arg)


# --end--

# 覆盖tk的Text控件
from tkinter.scrolledtext import ScrolledText as Text


# --end---
class Imgbutton:
	def __init__(self, root, width=100, img="", text="", command="", **arg):
		import tkinter as tk
		import PIL.Image
		import PIL.ImageTk
		self.img = PIL.ImageTk.PhotoImage(
			PIL.Image.open(img).resize(
				(width, width),
				PIL.Image.ANTIALIAS
			)
		)
		self.command = command
		self.Frame = tk.Frame(root)
		self.Label = tk.Label(self.Frame, text=text, image=self.img, compound="top", **arg)
		self.Label.bind("<Button-1>", self.command)
		self.Label.pack(fill="both", expand=True)

	# def command(self,*event):
	#     self.com()
	def configure(self, **arg):
		self.Label.configure(**arg)

	def pack(self, *K):
		self.Frame.pack(*K)

class ListBX:
	def __init__(self,root,*w,**arg):
		import tkinter as tk
		self.Frame = tk.Frame(root)
		# self.cmd = command
		self.get = tk.Scrollbar(self.Frame)
		self.ListBox = tk.ListBox(self.Frame, *w,yscrollcommand=self.get.set,**arg)
		self.get.config(command=self.ListBox.yview)
		self.ListBox.pack(side=tk.LEFT, fill=tk.BOTH,expand=True)
		self.get.pack(side=tk.RIGHT,fill=tk.X)
	def config(self,**kwargs):
		self.ListBox.config(**kwargs)
	def run(self,text:"str"):
		exec("self.ListBox."+text)
	def pack(self,*w,**kwargs):
		self.Frame.pack(*w,**kwargs)

# from tkinter import *


# from PIL import Image, ImageTk
# def inu(*event):
# 	print("click")
#
#
# def get():
# 	print(z.get())
# 	z.delete(0, END)
# 	z.insert(END, "wc牛逼")


# root = Tk()
# z = inpt_box(root, command=get, text="输入")
# z.insert(END, "wc牛逼")
# z.pack(fill=BOTH, expand=True)
# b = Text(root)
# b.pack(fill=BOTH, expand=True)
# appli = Imgbutton(root, img="img1.png", text="图片", command=inu)
# appli.pack()
# root.mainloop()




















