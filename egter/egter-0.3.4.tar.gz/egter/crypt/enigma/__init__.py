import random


def generate(seed):
	lst = {i: 0 for i in range(256)}
	used = []
	random.seed(seed)

	def g():
		r = random.randint(0,255)
		while r in used:
			r = random.randint(0,255)
		used.append(r)
		return r

	for i in range(128):
		gen = g()
		gen2 = g()
		lst[gen] = gen2
		lst[gen2] = gen

	return lst

def generate_configuration(seed, rotors=3):
	configuration = {'rotors': [generate(seed+bytes(i)) for i in range(rotors)], 'commutators': generate(seed+bytes(3))}
	return configuration


class Enigma:
	# TODO: add rotors move
	"""
		uses library random
		example:
		from egter.crypt import enigma
		e = enigma.Enigma(enigma.generate_configuration(b'pass'), b'pass')
		enc = e.encode(b'hello')
		dec = e.decode(enc)
		print(enc, dec)
		# b'\\xa7G&\\x1cP' b'hello'
	"""

	def __init__(self, configuration, seed, state=None, save_state=False):
		self.configuration = configuration
		# self.save_state = save_state
		# self.state = state
		self.seed = seed
		# if not state:
		# 	self.state = [0 for i in configuration['rotors']]
		# self.old_state = list(self.state)
		self.rotors_len = len(configuration['rotors'])

	# def rotor_down(self):
	# 	states = []
	# 	next_pl = False
	# 	self.state[0] += 1
	# 	for state in self.state:
	# 		if next_pl:
	# 			state += 1
	# 		if state > 255:
	# 			next_pl = True
	# 			state -= 256
	# 		else:
	# 			next_pl = False
	# 		states.append(state)
	# 	self.state = states

	# def rotor_up(self):
	# 	states = []
	# 	next_pl = False
	# 	self.state[0] -= 1
	# 	for state in self.state:
	# 		if next_pl:
	# 			state -= 1
	# 		if state < 0:
	# 			next_pl = True
	# 			state += 256
	# 		else:
	# 			next_pl = False
	# 		states.append(state)
	# 	self.state = states

	def get_byte(self, byte):
		tmp = byte
		for rotor in range(self.rotors_len):
			tmp = self.configuration['commutators'][tmp]
			tmp = self.configuration['rotors'][rotor][tmp]
			tmp = self.configuration['commutators'][tmp]
		lst = list(range(self.rotors_len))
		lst.reverse()
		# for rotor in lst:
		# 	tmp = self.configuration['commutators'][tmp]
		# 	print('->', 'rotor:', rotor, 'byte:', tmp, 'byte2:', self.configuration['rotors'][rotor][tmp])
		# 	tmp = self.configuration['rotors'][rotor][tmp]
		# 	tmp = self.configuration['commutators'][tmp]
		tmp += random.randint(0,255)
		if tmp > 255:
			tmp -= 256
		return tmp

	def get_byte_reverse(self, byte):
		tmp = byte
		tmp -= random.randint(0,255)
		if tmp < 0:
			tmp += 256
		lst = list(range(self.rotors_len))
		lst.reverse()
		for rotor in lst:
			tmp = self.configuration['commutators'][tmp]
			tmp = self.configuration['rotors'][rotor][tmp]
			tmp = self.configuration['commutators'][tmp]
		# for rotor in range(self.rotors_len):
		# 	tmp = self.configuration['commutators'][tmp]
		# 	print('->', 'rotor:', rotor, 'byte:', tmp, 'byte2:', self.configuration['rotors'][rotor][tmp])
		# 	tmp = self.configuration['rotors'][rotor][tmp]
		# 	tmp = self.configuration['commutators'][tmp]
		return tmp

	def encode(self, bt):
		random.seed(self.seed)
		bt = list(bytearray(bt))
		bts = []
		for byte in bt:
			byte = self.get_byte(byte)
			bts.append(byte)
		# if self.save_state == False:
		# 	self.state = self.old_state
		return bytes(bts)

	def decode(self, bt):
		random.seed(self.seed)
		bt = list(bytearray(bt))
		bts = []
		for byte in bt:
			byte = self.get_byte_reverse(byte)
			bts.append(byte)
		# if self.save_state == False:
		# 	self.state = self.old_state
		return bytes(bts)

class RandomCrypt:
	"""
		uses library random
		example:
		from egter.crypt import enigma
		e = enigma.RandomCrypt(b'pass')
		enc = e.encode(b'text')
		dec = e.decode(enc)
		print(enc, dec)
		# b'\\x07^\\x1b\\r' b'text'
	"""

	def __init__(self, password):
		self.password = password

	def encrypt(self, text):
		out = b''
		bt = list(text)
		random.seed(self.password)
		for letter in bt:
			letter += random.randint(0,255)
			if letter > 255:
				letter -= 256
			out += bytes([letter])
		return out

	def decrypt(self, text):
		out = b''
		bt = list(text)
		random.seed(self.password)
		for letter in bt:
			letter -= random.randint(0,255)
			if letter < 0:
				letter += 256
			out += bytes([letter])
		return out
