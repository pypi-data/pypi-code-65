from tensorflow.keras.datasets import mnist #Библиотека с базой Mnist
from tensorflow.keras.models import Sequential, Model # Подлючаем класс создания модели Sequential
from tensorflow.keras.layers import Dense, Input, Conv2D, Flatten, MaxPool2D # Подключаем класс Dense - полносвязный слой
from tensorflow.keras.optimizers import Adam # Подключаем оптимизатор Adam
from tensorflow.keras import utils #Утилиты для to_categorical
from tensorflow.keras.preprocessing import image #Для отрисовки изображения
import numpy as np # Подключаем библиотеку numpy
import pylab # Модуль для построения графиков
from mpl_toolkits.mplot3d import Axes3D # Модуль для трехмерной графики
from google.colab import files #Для загрузки своей картинки
import matplotlib.pyplot as plt #Отрисовка изображений
from PIL import Image #Отрисовка изображений
from IPython.display import clear_output
from tensorflow.keras.callbacks import LambdaCallback
import requests
from io import BytesIO
import tensorflow as tf
import warnings
import seaborn as sns
warnings.filterwarnings("ignore")
sns.set_style('darkgrid')

class MNIST_worker:
	def __init__(self):
		self.x_train_org = []
		self.y_train_org = []
		self.x_test_org = []
		self.y_test_org = []		
		self.x_train = []
		self.x_test = []
		self.y_train = []
		self.y_test = []
		self.firstLayer = True
		self.type_model = 0
		self.model = Sequential()    
		self.input_shape = (784,)
    

	def load_data(self):
		(self.x_train_org, self.y_train_org), (self.x_test_org, self.y_test_org) = mnist.load_data()
		clear_output(wait=True)
		#print('Загружены изображения рукописных цифр')
		print('Загружено ', self.x_train_org.shape[0],' обучающих изображений', sep='')
		print('Загружено ', self.x_test_org.shape[0],' тестовых изображений', sep='')
		print('Размер изображений: 28х28 пикселей' , sep='')		
		print()
		self.preproccess_images()
		self.dataset_shapes()
		return self.x_train, self.x_test, self.y_train, self.y_test

	def samples(self):		
		f,ax = plt.subplots(3,10, figsize=(20,6), gridspec_kw={'wspace':.1, 'hspace':0})
		for i in range (10):
			for j in range(3):
				x_temp = self.x_train_org[self.y_train_org == i]
				img = x_temp[np.random.randint(0, x_temp.shape[0])]
				ax[j, i].imshow(img, cmap='gray')
				ax[j, i].axis('off')
		plt.show()
	
	def preproccess_images(self):
		self.x_train = self.x_train_org.reshape(60000, 784)
		self.x_test = self.x_test_org.reshape(10000, 784)
		#Нормализуем входные картинки
		self.x_train = self.x_train.astype('float32') # преобразовываем x_train в тип float (цифры с плавающей точкой)
		self.x_train = self.x_train / 255 # делим на 255, чтобы диапазон был от 0 до 1
		self.x_test = self.x_test.astype('float32') # преобразовываем x_test в тип float (цифры с плавающей точкой)
		self.x_test = self.x_test / 255 # делим на 255, чтобы диапазон был от 0 до 1
		# Преобразуем ответы в формат one_hot_encoding
		self.y_train = utils.to_categorical(self.y_train_org, 10)
		self.y_test = utils.to_categorical(self.y_test_org, 10)
		print('Созданы обучающая и тестовая выборки')    

	
	def dataset_shapes(self):
		print('Размерность обучающей выборки  x_train:', self.x_train.shape)
		print('Размерность проверочной выборки x_test:', self.x_test.shape)
		print('Размерность y_train:', self.y_train.shape)
		print('Размерность  y_test:', self.y_test.shape)
		
	def create_model(self):    
		self.model.add(Dense(800, input_dim=784, activation="relu")) # Добавляем полносвязный слой на 800 нейронов с relu-активацией
		self.model.add(Dense(400, activation="relu")) # Добавляем полносвязный слой на 400 нейронов с relu-активацией
		self.model.add(Dense(10, activation="softmax")) # Добавляем полносвязный слой на 10 нейронов с softmax-активацией
		print('Создана модель нейронной сети.')
		print('Схема созданной модели:')
		self.model.summary()
		
	def createModel(self, tp):
		if (tp == 'Полносвязная'):
		  self.input_shape = (784,) 
		  self.type_model=0         
		else:
		  self.input_shape = (28,28,1)
		  self.type_model=1    
		self.model = Sequential()  
	
	def addLayer(self, typeLayer = 'Полносвязный', countNeurons = 128, kernelSize=(2,2), act='relu'):
		kwargs={'activation' : act}		
		if self.firstLayer:      
			kwargs.update({'input_shape':self.input_shape})
			self.firstLayer = False			
		if self.type_model == 1 and typeLayer=='Сверточный слой':
		  kwargs.update({'kernel_size':kernelSize})
		if self.type_model == 1 and typeLayer=='МаксПуллинг слой':
		  kwargs = {'pool_size':kernelSize}
		if self.type_model == 1 and act=='softmax':
		  self.model.add(Flatten())
		if (typeLayer=='Полносвязный слой'):
		  kwargs.update({'units' : countNeurons})
		  self.model.add(Dense(**kwargs))
		if typeLayer=='Сверточный слой':
		  kwargs.update({'filters' : countNeurons})
		  self.model.add(Conv2D(**kwargs))
		if typeLayer=='МаксПуллинг слой':
		  self.model.add(MaxPool2D(**kwargs))

	
	
	def set_model(self, model):
		self.model = model
		
	def train_model(self, batch_size, epochs, val_split):
		if (self.type_model==1):
			self.x_train = np.reshape(self.x_train, (-1, 28,28,1))
			self.x_test = np.reshape(self.x_test, (-1, 28,28,1))
		acc = []
		val_acc = []
		def on_epoch_end(epoch, log):
			count = 2
			if epoch >= 9:
				count = 1
			if epoch >= 99: 
				count = 0
			s = "* Эпоха:" + str(epoch+1) + ' '* count
			s += " | Точность (обучающая выборка): " + str(round(log['accuracy'] * 100, 2)) + '%'			
			l = len(s)
			s += ' ' * (55 - l) + "Точность (проверочная выборка): " + str(round(log['val_accuracy']* 100 ,2)) + '%'
			acc.append(log['accuracy'])
			val_acc.append(log['val_accuracy'])
			print(s)
		
		mnist_cb = LambdaCallback(on_epoch_end=on_epoch_end)		
		self.model.compile(loss="categorical_crossentropy", optimizer="adam", metrics=["accuracy"])
		self.model.fit(self.x_train, self.y_train, batch_size=batch_size, epochs = epochs, validation_split=val_split, callbacks=[mnist_cb], verbose=0)
		plt.figure(figsize=(14,7))
		plt.plot(acc, label = 'Обучающая выборка')
		plt.plot(val_acc, label = 'Проверочная выборка')
		plt.title('График точности')
		plt.xlabel('Эпоха')
		plt.ylabel('Точность')
		plt.legend()
		plt.show()
		
	def predict(self, *args):
		for i in args:
			x_temp = self.x_test[self.y_test_org == i]
			idx = np.random.randint(0, x_temp.shape[0])
			plt.imshow(x_temp[idx].reshape(28,28), cmap='gray')
			sample = np.expand_dims(x_temp[idx], 0)
			predict = self.model.predict(sample)[0]
			plt.axis('off')
			plt.show()
			print('Распознана цифра:')
			for i in range(10):
			  print('Цифра ', i, ': ', round(predict[i]*100,2),'%', sep='')	
			print()
			print()
			print()

	def loadImage(self, URL):
		response = requests.get(URL)
		img = Image.open(BytesIO(response.content))
		img.save('example.jpg')  

	def predict_from_file(self, filename, color_inverse):    
		self.loadImage(filename)
		f = image.load_img('example.jpg', target_size=(28,28), color_mode = 'grayscale')
		sample = np.array(f)
		plt.imshow(sample, cmap='gray')
		plt.axis('off')
		plt.show()
		if self.type_model==0:
		  sample = np.reshape(sample, (-1, 784))
		else:
		  sample = np.reshape(sample, (-1, 28, 28, 1))
		sample = sample.astype('float32')
		if color_inverse:
			sample = 255 - sample
		sample /= 255    			
		predict = self.model.predict(sample)[0]
		print('Распознана цифра:')
		for i in range(10):
		  print('Цифра ', i, ': ', round(predict[i]*100,2),'%', sep='')	
		
		
worker = MNIST_worker()

def load_data():
	worker.load_data()
	
def samples():
	worker.samples()
def preproccess_images():
	worker.preproccess_images()
	
def dataset_info():
	worker.dataset_shapes()

def create_default_model():
	worker.create_model()

def set_model(model):
	worker.set_model(model)
	
def train_model(batch_size=128, epochs = 15, val_split=0.2):
	worker.train_model(batch_size, epochs, val_split)
	
def predict(*args):
	worker.predict(*args)

def predict_from_file(filename, color_inverse = False):
  worker.predict_from_file(filename, color_inverse)

def createModel(tp):
	worker.createModel(tp)

def addLayer(typeLayer = 'Dense', countNeurons = 128, kernelSize=(2,2)):
	worker.addLayer(typeLayer, countNeurons,kernelSize)

def addOutLayer(typeLayer = 'Dense', countNeurons = 128, kernelSize=(2,2)):
	worker.addLayer(typeLayer, countNeurons,kernelSize, 'softmax')
	print('*** Нейронная сеть создана ***')
	print('Схема нейронной сети:')
	tf.keras.utils.plot_model(worker.model, to_file='scheme.png', show_shapes=True)
	image = plt.imread('scheme.png')
	plt.figure(figsize=(8,8))
	plt.imshow(image)
	plt.axis('off')
	plt.show()
	worker.firstLayer = True
