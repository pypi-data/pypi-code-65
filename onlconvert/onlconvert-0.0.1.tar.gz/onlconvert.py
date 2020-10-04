from PIL import Image

class imgconvert:

	def __init__(self, name):
		self.img = Image.open(name)

	def jpg(self, filename):
		img = self.img.convert('RGB')
		img.save(f'{filename}.jpg', "jpeg")

	def png(self, filename):
		img = self.img.convert('RGBA')
		img.save(f'{filename}.png', "png")

	def webp(self, filename):
		self.img.save(f'{filename}.webp', "webp")

	def ico(self, filename):
		self.img.save(f'{filename}.ico', "ico")

	def pdf(self, filename):
		self.img.save(f'{filename}.pdf', "pdf")

class textconvert:

	def __init__(self, name):
		with open(name, 'r') as file:
			self.content = file.read()

	def txt(self, filename):
		self.textfile = open(f'{filename}.txt', 'a')
		self.textfile.write(self.content)
		self.textfile.close()

	def doc(self, filename):
		self.textfile = open(f'{filename}.doc', 'a')
		self.textfile.write(self.content)
		self.textfile.close()
		
	def docx(self, filename):
		self.textfile = open(f'{filename}.docx', 'a')
		self.textfile.write(self.content)
		self.textfile.close()

	def html(self, filename):
		self.textfile = open(f'{filename}.html', 'a')
		self.textfile.write(self.content)
		self.textfile.close()

	def rtf(self, filename):
		self.textfile = open(f'{filename}.rtf', 'a')
		self.textfile.write(self.content)
		self.textfile.close()

	def otd(self, filename):
		self.textfile = open(f'{filename}.otd', 'a')
		self.textfile.write(self.content)
		self.textfile.close()