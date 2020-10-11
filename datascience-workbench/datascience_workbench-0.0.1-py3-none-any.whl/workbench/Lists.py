class Lists:

	def __init__(self):
		""" Convenient methods to modify, process and create lists 
		"""

	def flatten(nested_list):
		"""Flattens nested list"""
		return [element for sublist in nested_list for element in sublist]

	def remove_duplicates(l):
		"""Removes duplicates from list elements whilst preserving element order

		Input
			list with string elements

		Return 
			Sorted list without duplicates

		"""
		return list(dict.fromkeys(l))

	def string_manual_correction(x):
		"""Traverse a list of strings and correct entries manually
		Can be applied to pandas Series object

		Input
			x: list with keywords to manually correct

		Return
			list: manually corrected list

		"""

		print("Correct strings manually. \n\
		\t1. Go forward with ENTER \n\
		\t2. Go backwards by typing the backwardsstep number.\n\
		\tExit by typing 'exit'")
	    
		i = 0
		while i < len(x):
			correction = input("{}\t {} >>>".format(i, x[i]))

			## navigate in integer steps
			# when integer specified, change index 
			if correction.isnumeric():
				i -= int(correction)

			elif correction == 'exit':
				i = len(x)

			elif len(correction) > 0 and correction != 'exit':
				x[i] = correction
				i += 1

			# if nothing specified go 1 step forward 
			else:
				i += 1

		return x



def batch(lst, n=5):
		"""Yield successive n-sized chunks from list lst

		adapted from https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks

		Input
		lst: list 
		n: selected batch size

		Return 
		List: Nested list with length (len(lst)/n) divided into n-sized batches
		"""

		batched_list = []

		for i in range(0, len(lst), n):
			batched_list.append(lst[i:i + n])

		return batched_list
