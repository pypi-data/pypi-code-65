import tempfile
import importlib.util

from .model_list_generator import generate


class TestModelGeneration:

    def setup_class(self):
        _, tmp_file = tempfile.mkstemp(suffix='.py')
        # We check no exception is raised
        generate(tmp_file)

        # We try to load the generated module
        spec = importlib.util.spec_from_file_location("module.name", tmp_file)
        self.model_list_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.model_list_module)

    def test_generate_is_not_empty(self):
        # We do simple checks to verify the model list has the expected structure
        assert "image_detection.pretraining_natural_rgb.faster_rcnn.resnet_50_v1" in self.model_list_module.model_list

    def test_generated_args(self):
        for key, model_args in self.model_list_module.model_list.items():
            key = key.split('.')
            if key[1] != 'pretraining_none':
                assert 'pretrained_parameters' in model_args.default_args['trainer'], "Missing pretrained parameters in: '{}'".format(key)
