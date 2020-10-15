import pandas as pd
import os
import glob

class Processing:

  def __init__(self):

  	""" Class with methods to handle data processing 
  	"""



  def get_files(filepath):
    """List all files within filepath
    Args
      filepath: string specifying folder

    Return
      list: string list elements with filenames 
    
    """
    all_files = []
    for root, dirs, files in os.walk(filepath):
        files = glob.glob(os.path.join(root,'*.json'))
        for f in files :
            all_files.append(os.path.abspath(f))

    return all_files



  def make_csv(x, filename, data_dir, append=False, header=False, index=False):
    '''Merges features and labels and converts them into one csv file with labels in the first column
    
    	Input
       		x: Data features
       		file_name: Name of csv file, ex. 'train.csv'
       		data_dir: The directory where files will be saved
       	
       	Return
       		None: Create csv file as specified
    '''
    
    # create dir if nonexistent
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # make sure its a df
    x = pd.DataFrame(x)
    
    # export to csv
    if not append:
        x.to_csv(os.path.join(data_dir, filename), 
                                     header=header, 
                                     index=index)
    # append to existing
    else:
        x.to_csv(os.path.join(data_dir, filename),
                                     mode = 'a',
                                     header=header, 
                                     index=index)        
    
    # nothing is returned, but a print statement indicates that the function has run
    print('Path created: '+str(data_dir)+'/'+str(filename))
      