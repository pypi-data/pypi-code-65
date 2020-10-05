import sys
import time

class LoadPy:
	
	def __init__(self, name):
		
		self.name = name


	def animate(self):
		if self.name == "default":
			l = ['|', '/', '-', '\\']
			for i in l+l+l:
				sys.stdout.write('\r' + '[*] Loading... '+i)
				sys.stdout.flush()
				time.sleep(0.2)

		if self.name == "miniload":
			l = ["[■□□□□□□□□□]","[■■□□□□□□□□]", "[■■■□□□□□□□]", "[■■■■□□□□□□]", "[■■■■■□□□□□]", "[■■■■■■□□□□]", "[■■■■■■■□□□]", "[■■■■■■■■□□]", "[■■■■■■■■■□]", "[■■■■■■■■■■]"]
			for i in l:
				sys.stdout.write('\r' + i)
				sys.stdout.flush()
				time.sleep(0.2)


		if self.name == "bigload":
			# █
			# l = 
			for i in ["[█         ]","[██        ]", "[███       ]", "[████      ]", "[█████     ]", "[██████    ]", "[███████   ]", "[████████  ]", "[█████████ ]", "[█████████]"]:
				sys.stdout.write('\r' + i)
				sys.stdout.flush()
				time.sleep(0.2)