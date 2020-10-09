import chainer
import chainer.links as L
import chainer.functions as F

from chainer_addons.links import DeConv2D_BN
from chainer_addons.links.pooling import PoolingType

from functools import partial

class InceptionHeadDecoder(chainer.Chain):

	def __init__(self, in_channels=192, out_channels=3,
		chans=[80, 64, 32, 32], set_outsize=True):
		super(InceptionHeadDecoder, self).__init__()


		with self.init_scope():
			# input 192 x 35 x 35
			self.unpool7 = partial(F.unpooling_2d, ksize=3, stride=2, pad=0,
				outsize=(71, 71) if set_outsize else None)
			i = 0
			# input 192 x 71 x 71
			self.deconv6 = DeConv2D_BN(in_channels, chans[i], ksize=3,
				outsize=(73, 73) if set_outsize else None)
			# input 80 x 73 x 73
			self.deconv5 = DeConv2D_BN(chans[i], chans[i+1], ksize=1,
				outsize=(73, 73) if set_outsize else None)
			i += 1
			# input 64 x 73 x 73
			self.unpool4 = partial(F.unpooling_2d, ksize=3, stride=2, pad=0,
				outsize=(147, 147) if set_outsize else None)
			# input 64 x 147 x 147
			self.deconv3 = DeConv2D_BN(chans[i], chans[i+1], ksize=3, pad=1,
				outsize=(147, 147) if set_outsize else None)
			i += 1
			# input 32 x 147 x 147
			self.deconv2 = DeConv2D_BN(chans[i], chans[i+1], ksize=3,
				outsize=(149, 149) if set_outsize else None)
			i += 1
			# input 32 x 149 x 149
			self.deconv1 = DeConv2D_BN(chans[i], out_channels, ksize=3, stride=2,
				outsize=(299, 299) if set_outsize else None)
			# output 3 x 299 x 299

	def __call__(self, x):
		assert x.shape[2:] == (35, 35), \
			f"Invalid input shape: {(35, 35)} != {x.shape[2:]}"
		x = self.unpool7(x)
		x = self.deconv6(x)
		x = self.deconv5(x)
		x = self.unpool4(x)
		x = self.deconv3(x)
		x = self.deconv2(x)
		x = self.deconv1(x)

		return x

class Inception1Decoder(chainer.Chain):

	def __init__(self, in_channels, out_channels, outsize=(35, 35), **pool_args):
		super(Inception1Decoder, self).__init__()

		with self.init_scope():

			self.deconv = DeConv2D_BN(in_channels, out_channels,
				ksize=3, pad=1, outsize=outsize)

			# self.deconv1x1   = DeConv2D_BN(in_channels, ???, ksize=1,
			# 	outsize=outsize)

			# self.deconv5x5_1 = DeConv2D_BN(in_channels, ???, ksize=1,
			# 	outsize=outsize)
			# self.deconv5x5_2 = DeConv2D_BN(in_channels, ???, ksize=5, pad=2,
			# 	outsize=outsize)

			# self.deconv3x3_1 = DeConv2D_BN(in_channels, ???, ksize=1,
			# 	outsize=outsize)
			# self.deconv3x3_2 = DeConv2D_BN(in_channels, ???, ksize=3, pad=1,
			# 	outsize=outsize)
			# self.deconv3x3_2 = DeConv2D_BN(in_channels, ???, ksize=3, pad=1,
			# 	outsize=outsize)

			# self.pool_deconv = DeConv2D_BN(in_channels, ???, ksize=1,
			# 	outsize=outsize)

			# input in_c x 35 x 35
			# self.unpool4 = partial(F.unpooling_2d, **pool_args)

	def __call__(self, x):

		return self.deconv(x)


class Inception2Decoder(chainer.Chain):

	def __init__(self, in_channels, out_channels, outsize=(35, 35), **pool_args):
		super(Inception2Decoder, self).__init__()

		with self.init_scope():

			self.deconv = DeConv2D_BN(in_channels, out_channels,
				ksize=3, stride=2, outsize=outsize)

	def __call__(self, x):
		return self.deconv(x)

class Inception3Decoder(chainer.Chain):

	def __init__(self, in_channels, out_channels, chans=None, outsize=(17, 17), **pool_args):
		super(Inception3Decoder, self).__init__()
		chans = chans or in_channels

		with self.init_scope():
			self.deconv0 = DeConv2D_BN(in_channels, chans,
				ksize=(7, 1), pad=(3, 0), outsize=outsize)

			self.deconv1 = DeConv2D_BN(chans, out_channels,
				ksize=(1, 7), pad=(0, 3), outsize=outsize)

	def __call__(self, x):
		x = self.deconv0(x)
		x = self.deconv1(x)
		return x

class Inception4Decoder(chainer.Chain):

	def __init__(self, in_channels, out_channels, chans=None, outsize=(17, 17), **pool_args):
		super(Inception4Decoder, self).__init__()
		chans = chans or in_channels

		with self.init_scope():
			self.deconv0 = DeConv2D_BN(in_channels, chans,
				ksize=3, stride=2, outsize=outsize)

			self.deconv1 = DeConv2D_BN(chans, chans,
				ksize=(7, 1), pad=(3, 0), outsize=outsize)

			self.deconv2 = DeConv2D_BN(chans, out_channels,
				ksize=(1, 7), pad=(0, 3), outsize=outsize)

	def __call__(self, x):
		x = self.deconv0(x)
		x = self.deconv1(x)
		x = self.deconv2(x)
		return x


class Inception5Decoder(chainer.Chain):

	def __init__(self, in_channels, out_channels, chans=None, outsize=(8, 8), **pool_args):
		super(Inception5Decoder, self).__init__()
		chans = chans or in_channels

		with self.init_scope():

			self.deconv0 = DeConv2D_BN(in_channels, chans,
				ksize=(3, 1), pad=(1, 0), outsize=outsize)

			self.deconv1 = DeConv2D_BN(chans, chans,
				ksize=(1, 3), pad=(0, 1), outsize=outsize)

			self.deconv2 = DeConv2D_BN(chans, out_channels,
				ksize=3, pad=1, outsize=outsize)

	def __call__(self, x):
		x = self.deconv0(x)
		x = self.deconv1(x)
		x = self.deconv2(x)
		return x

if __name__ == '__main__':
	import numpy as np
	from tabulate import tabulate

	chainer.config.train = False
	chainer.enable_backprop = False

	x = np.random.normal(size=(2, 2048, 8, 8)).astype(dtype=np.float32)

	_links = [

		("mixed10", Inception5Decoder(2048, 2048)),
		("mixed09", Inception5Decoder(2048, 1280)),

		("mixed08", Inception4Decoder(1280, 768)),

		("mixed07", Inception3Decoder( 768, 768)),
		("mixed06", Inception3Decoder( 768, 768)),
		("mixed05", Inception3Decoder( 768, 768)),
		("mixed04", Inception3Decoder( 768, 768)),

		("mixed03", Inception2Decoder( 768, 288)),

		("mixed02", Inception1Decoder( 288, 288)),
		("mixed01", Inception1Decoder( 288, 256)),
		("mixed00", Inception1Decoder( 256, 192)),

		("head", InceptionHeadDecoder()),
	]

	rows = []
	for name, l in _links:
		row = (name, x.shape)
		x = l(x)
		row += (x.shape,)

		rows.append(row)

	print(tabulate(rows,
		headers=("Name", "InShape", "OutShape"),
		tablefmt="fancy_grid"))

