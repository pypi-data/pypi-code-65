"""Init for utils."""
from .graph_utils import load_graph, pb_to_tensorboard_event, freeze_session, freeze_graph_from_ckpt, wrap_frozen_graph
from .tf_runner import TFRunner, TFRunnerOld
from .runner import Runner

__all__ = [
    'Runner',
    'TPURunner',
    'load_graph',
    'pb_to_tensorboard_event',
    'freeze_session',
    'freeze_graph_from_ckpt',
    'wrap_frozen_graph',
    'TFRunner',
    'TFRunnerOld',
]

try:
    from .tpu_runner import TPURunner

    __all__.append('TPURunner')
except ImportError as exception:
    print(f'Warning: {exception}')
