class Crypter:

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
