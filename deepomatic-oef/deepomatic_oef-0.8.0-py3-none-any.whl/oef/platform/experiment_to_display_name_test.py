from deepomatic.oef.protos.models.image.backbones_pb2 import EfficientNetBackbone

from .experiment_to_display_name import CustomFormatter


def test_custom_formatter():
    class Foo:
        @property
        def x(self):
            return 1

        @property
        def y(self):
            return 2

    backbone = EfficientNetBackbone(version=EfficientNetBackbone.Version.B1)

    fmt = CustomFormatter()
    assert fmt.format('hello {version} {survival_prob}', backbone) == 'hello 1 0.8'
    assert fmt.format('hello {version:backbones_pb2.EfficientNetBackbone.Version} {survival_prob}', backbone) == 'hello B1 0.8'
    assert fmt.format('hello {version:backbones_pb2.EfficientNetBackbone.Version,lower} {survival_prob}', backbone) == 'hello b1 0.8'
    assert fmt.format('hello {version}{survival_prob:not(0.8),concat_before( )}', backbone) == 'hello 1'
    assert fmt.format('hello {version}{survival_prob:not(0.7),concat_before( )}', backbone) == 'hello 1 0.8'
    assert fmt.format('hello {version} {survival_prob:.0%}', backbone) == 'hello 1 80%'
