class Crypter:

	def encrypt(text, password):
		if type(password) is str:
			psw = 0
			for x in range(len(password)):
				psw += ord(password[-(x + 1)]) * (x + 1)

		elif type(password) is int:
			psw = password

		else:
			return None

		output_text = ''

		for x in text:
			output_text += chr(ord(x) + (psw % len(text)) + 1)
			psw += psw % len(text) + int(ord(x) / 2)

		return output_text

	def decrypt(text, password):
		if type(password) is str:
			psw = 0
			for x in range(len(password)):
				psw += ord(password[-(x + 1)]) * (x + 1)

		elif type(password) is int:
			psw = password

		else:
			return None

		output_text = ''

		for x in text:
			output_text += chr(ord(x) - (psw % len(text) + 1))
			psw += psw % len(text) + int((ord(x) - (psw % len(text) + 1)) / 2)

		return output_text

	def encrypt_caesar_cipher(text, password):
		if type(password) is str:
			psw = 0
			for x in range(len(password)):
				psw += ord(password[-(x + 1)]) * (x + 1)

		elif type(password) is int:
			psw = password

		else:
			return None

		output_text = ''

		for x in text:
			output_text += chr(ord(x) + psw)

		return output_text

	def decrypt_caesar_cipher(text, password):
		if type(password) is str:
			psw = 0
			for x in range(len(password)):
				psw += ord(password[-(x + 1)]) * (x + 1)

		elif type(password) is int:
			psw = password

		else:
			return None

		output_text = ''

		for x in text:
			output_text += chr(ord(x) - psw)

		return output_text
