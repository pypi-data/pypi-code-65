import traceback

# Caesar Cipher
SYMBOLS_2 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
SYMBOLS_RU = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя"


class cipher:

	def getTranslatedMessage(mode=True, SYMBOLS, message, key):		
		if mode[0] is True:		
			key = -key		
		translated = ''		
			
		for symbol in message:		
			symbolIndex = SYMBOLS.find(symbol)		
			if symbolIndex == -1: # Symbol not found in SYMBOLS.		
				# Just add this symbol without any change.		
				translated += symbol		
			else:		
				# Encrypt or decrypt		
				symbolIndex += key		
			
				if symbolIndex >= len(SYMBOLS):		
					symbolIndex -= len(SYMBOLS)		
				elif symbolIndex < 0:		
					symbolIndex += len(SYMBOLS)		
			
				translated += SYMBOLS[symbolIndex]		
		return print(translated)