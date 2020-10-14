import math

from chainer.dataset import Iterator
from tqdm import tqdm

class ProgressBarWrapper(Iterator):

	def __init__(self, it, *args, **kwargs):
		super(ProgressBarWrapper, self).__init__()

		self._orig_it = it
		self.args = args
		self.kwargs = kwargs
		self._iter = None

	def __iter__(self):
		return self.iter

	def reset(self):
		self._orig_it.reset()
		self._iter = None

	@property
	def iter(self):
		if self._iter is None:
			self._iter = iter(tqdm(self._orig_it, total=self.n_batches,
				*self.args, **self.kwargs))
		return self._iter

	@property
	def n_batches(self):
		return int(math.ceil(len(self._orig_it.dataset) // self._orig_it.batch_size))

	@property
	def dataset(self):
		return self._orig_it.dataset

	@property
	def batch_size(self):
		return self._orig_it.batch_size

	def __next__(self):
		return next(self.iter)

	def serialize(self, serializer):
		return self._orig_it.serialize(serializer)
