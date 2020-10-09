import os
import getpass
import time
import hashlib
import numpy as np
import warnings

from .inputs import PredefinedField

class Cache:
	def __init__(self,
		root = '\\\\share.ipp-hgw.mpg.de/mp',
		dir = 'fieldline/{user}/fieldlinetracer/field_cache',
		max_age = 7 * 24 * 60 * 60
	):
		self.user = getpass.getuser()
		self.dir = dir.format(user = self.user)
		self.root = root
		
		self.max_age = max_age;
		
		self.maintenance();	
	
	def maintenance(self):
		root = self.cache_root();
		
		if not os.path.exists(root):
			os.makedirs(root);
		
		for filename in os.listdir(root):
			fullname = os.path.join(root, filename);
			
			age = time.time() - os.path.getmtime(fullname);
			
			if age > self.max_age:
				os.remove(fullname);
	
	def cache_root(self):
		return os.path.join(*(self.root.split('/')), *(self.dir.split('/')))
	
	def exists(self, id):
		return os.path.exists(self.filename(id));
	
	def filename(self, id):
		return os.path.join(self.cache_root(), id)
	
	def remote_reference(self, id):
		return '/' + self.dir + '/' + id

try:
	cache = Cache()
except Exception as e:
	warnings.warn('Cache initialization failed for the following reason, faster field transfer will not be available')
	print(e)
	
	cache = None

def maybe_cache_config(config, cache = cache):
	if not isinstance(config, PredefinedField):
		return None
	
	if cache is None:
		return None
	
	try:
		cache.maintenance()
		
		flat_view = np.reshape(config.field, [3, -1])
		id = hashlib.sha1(flat_view).hexdigest()
		
		if not cache.exists(id):
			filename = cache.filename(id)
			pre_filename = filename + '.tmp'
			
			#print('Writing temp file {} ...'.format(pre_filename))
			
			with open(pre_filename, 'w') as file:
				for i in range(0, flat_view.shape[1]):
					file.write('{bp} {br} {bz}\n'.format(
						bp = flat_view[0, i],
						br = flat_view[1, i],
						bz = flat_view[2, i]
					));
						
			os.rename(pre_filename, filename)
			#print('Renamed temp file {} to {} ...'.format(pre_filename, filename))
		
		return cache.remote_reference(id)
	except Exception as e:
		warnings.warn('Failed to access the field cache for the following reason, falling back to slower direct transfer')
		print(e)
	
	return None