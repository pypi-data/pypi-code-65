import chainer
import numpy as np

from chainer.serializers import npz
from chainer_addons.models.base import PretrainedModelMixin
from chainercv.transforms import resize
from chainercv.transforms import scale
from chainercv2.models.efficientnet import efficientnet_b4c

from collections.abc import Iterable

class EfficientNetLayers(PretrainedModelMixin, chainer.Chain):

	class meta:
		input_size = 380
		n_conv_maps = 1792
		feature_size = 1792
		conv_map_layer = "final_block"
		feature_layer = "final_pool"
		classifier_layers = ["fc"]
		mean = np.array([.5, .5, .5], dtype=np.float32).reshape(-1, 1, 1)
		std = np.array([.5, .5, .5], dtype=np.float32).reshape(-1, 1, 1)

		@staticmethod
		def prepare_func(x, size=None, swap_channels=True, keep_ratio=True, *args, **kwargs):
			if size is None:
				size = EfficientNetLayers.meta.input_size
				size = (size, size)

			# [0..255] -> [0..1]
			x = x.astype(np.float32) / 255

			# HWC -> CHW channel order
			x = x.transpose(2,0,1)

			if keep_ratio:
				if isinstance(size, Iterable):
					size = min(size)
				# scale the smallest side to <size>
				x = scale(x, size=size)
			else:
				if isinstance(size, int):
					size = (size, size)

				# resize the image to  side to <size>x<size>
				x = resize(x, size)

			if swap_channels:
				x = x[::-1]

			# [0..1] -> [-0.5 .. 0.5]
			x -= EfficientNetLayers.meta.mean
			# [-0.5 .. 0.5] -> [-1 .. 1]
			x /= EfficientNetLayers.meta.std

			return x

	@property
	def _links(self):
		assert getattr(self, "net", None) is not None, \
			"layers were not initialized yet!"
		links = []

		features = self.net.features
		for i, name in enumerate(features.layer_names):
			links.append((name,  [features[name]]))

		output = self.net.output
		links.extend([
			("flatten", [output.flatten, output.dropout]),
			("fc",      [output.fc]),
		])

		return links

	@property
	def fc(self):
		return self.net.output.fc

	@fc.setter
	def fc(self, value):
		self.net.output.fc = value

	def init_layers(self, n_classes):
		self.net = efficientnet_b4c()

	def load(self, weights, strict=False, headless=False):
		if weights in [None, "auto"]:
			return

		ignore_names = None
		if headless:
			ignore_names = lambda name: name.startswith(self.clf_layer_name)

		npz.load_npz(weights, self.net, strict=strict, ignore_names=ignore_names)


	def __call__(self, x, layer_name="fc"):
		for key, funcs in self.functions.items():

			for func in funcs:
				x = func(x)

			if key == layer_name:
				return x
