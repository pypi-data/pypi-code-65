import pandas as pd
import numpy as np


def read_sample(filename, sample_size, verbose =False, **kwargs):

	"""

    Parameters
    ----------
    
    filename: csv file tipe
	sample_size: if value is less than 1 
	verbose: if true, it will print all reading and sampling stages
    kwargs: all other parameters from pandas.read_csv() function

    values
    ------  
     """
	

	n = sum(1 for line in open(filename)) - 1 #number of records in file (excludes header)

	if verbose:
		print((str(n) + ' total lines to read'))

	assert sample_size>0

	if sample_size<1:
		s = int(sample_size*n) #desired sample size
	else:
		s=sample_size

	if verbose:
		print((str(s) + ' samples'))

	skip = np.sort(np.random.choice(range(1, n+1),n-s)) #the 0-indexed header will not be included in the skip list
	
	df = pd.read_csv(filename, skiprows=skip, nrows=s, **kwargs)




