import chainer
import chainer.functions as F
import chainer.links as L

from os.path import isfile

from chainer_addons.models.base import PretrainedModelMixin
from chainer_addons.models.inception.decoder import blocks


class InceptionV3Decoder(PretrainedModelMixin, chainer.Chain):
	class meta:
		input_size = 299
		feature_size = 2048
		n_conv_maps = 2048

	def __init__(self, pretrained_model=None, *args, **kwargs):
		super(InceptionV3Decoder, self).__init__(*args, **kwargs)

		if pretrained_model is not None and isfile(pretrained_model):
			self.load(pretrained_model, strict=True)

	def init_layers(self, *args, **kwargs):
		# input 2048 x 8 x 8
		self.mixed10 = blocks.Inception5Decoder(2048, 2048, chans=512)
		# input 2048 x 8 x 8
		self.mixed09 = blocks.Inception5Decoder(2048, 1280, chans=256)
		# input 1280 x 8 x 8
		self.mixed08 = blocks.Inception4Decoder(1280, 768, chans=128)
		# input 768 x 17 x 17
		self.mixed07 = blocks.Inception3Decoder( 768, 768, chans=128)
		# input 768 x 17 x 17
		self.mixed06 = blocks.Inception3Decoder( 768, 768, chans=128)
		# input 768 x 17 x 17
		self.mixed05 = blocks.Inception3Decoder( 768, 768, chans=128)
		# input 768 x 17 x 17
		self.mixed04 = blocks.Inception3Decoder( 768, 768, chans=128)
		# input 768 x 17 x 17
		self.mixed03 = blocks.Inception2Decoder( 768, 288)
		# input 288 x 35 x 35
		self.mixed02 = blocks.Inception1Decoder( 288, 288)
		# input 288 x 35 x 35
		self.mixed01 = blocks.Inception1Decoder( 288, 256)
		# input 256 x 35 x 35
		self.mixed00 = blocks.Inception1Decoder( 256, 192)
		# input 192 x 35 x 35
		self.head = blocks.InceptionHeadDecoder( 192,   3)
		# output 3 x 299 x 299

	@property
	def _links(self):
		return [
			("mixed10", [self.mixed10]),
			("mixed09", [self.mixed09]),
			("mixed08", [self.mixed08]),
			("mixed07", [self.mixed07]),
			("mixed06", [self.mixed06]),
			("mixed05", [self.mixed05]),
			("mixed04", [self.mixed04]),
			("mixed03", [self.mixed03]),
			("mixed02", [self.mixed02]),
			("mixed01", [self.mixed01]),
			("mixed00", [self.mixed00]),
			("head",    [self.head]),
		]

	def generate(self, x):
		x = self.mixed10(x)
		x = self.mixed09(x)
		x = self.mixed08(x)
		x = self.mixed07(x)
		x = self.mixed06(x)
		x = self.mixed05(x)
		x = self.mixed04(x)
		x = self.mixed03(x)
		x = self.mixed02(x)
		x = self.mixed01(x)
		x = self.mixed00(x)
		x = self.head(x)
		return x

	def __call__(self, x, *args, **kwargs):
		return self.generate(x)

	def loss(self, pred, gt, loss_func=F.mean_squared_error):
		pass


if __name__ == '__main__':
	from chainer_addons import utils
	model = InceptionV3Decoder(pretrained_model="auto")

	var = model.xp.random.normal(size=(2, 2048, 8, 8)).astype(model.xp.float32)
	utils.print_model_info(model, input_var=var)
