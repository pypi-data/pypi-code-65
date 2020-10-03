# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tf_raft', 'tf_raft.datasets', 'tf_raft.layers', 'tf_raft.losses']

package_data = \
{'': ['*']}

install_requires = \
['albumentations>=0.4.6,<0.5.0',
 'tensorflow-addons>=0.11.1,<0.12.0',
 'tensorflow>=2.3.0,<3.0.0']

setup_kwargs = {
    'name': 'tf-raft',
    'version': '0.1.4',
    'description': 'RAFT (Recurrent All Pairs Field Transforms for Optical Flow) implementation via tf.keras',
    'long_description': "# tf-raft\nRAFT (Recurrent All Pairs Field Transforms for Optical Flow, Teed et. al., ECCV2020) implementation via tf.keras\n\n## Original resources\n- [RAFT: Recurrent All Pairs Field Transforms for Optical Flow](https://arxiv.org/abs/2003.12039)\n- https://github.com/princeton-vl/RAFT\n\n## Installation\n\n```\n$ pip install tf-raft\n```\n\nor you can simply clone this repository.\n\n### Dependencies\n- TensorFlow\n- TensorFlow-addons\n- albumentations\n\nsee details in `pyoroject.toml`\n\n## Optical flow datasets\n[MPI-Sintel](http://sintel.is.tue.mpg.de/) or [FlyingChairs](https://lmb.informatik.uni-freiburg.de/resources/datasets/FlyingChairs.en.html#flyingchairs) datasets are relatively light. See more datasets in the [oirignal repository](https://github.com/princeton-vl/RAFT)\n\n## Usage\n\n``` python\nfrom tf_raft.model import RAFT, SmallRAFT\nfrom tf_raft.losses import sequence_loss, end_point_error\n\n# iters/iters_pred are the number of recurrent update of flow in training/prediction\nraft = RAFT(iters=iters, iters_pred=iters_pred)\nraft.compile(\n    optimizer=optimizer,\n    clip_norm=clip_norm,\n    loss=sequence_loss,\n    epe=end_point_error\n)\n\nraft.fit(\n    ds_train,\n    epochs=epochs,\n    callbacks=callbacks,\n    steps_per_epoch=train_size//batch_size,\n    validation_data=ds_val,\n    validation_steps=val_size\n)\n```\n\nIn practice, you are required to prepare dataset, optimizer, callbacks etc, check details in `train_sintel.py` or `train_chairs.py`.\n\n### Train via YAML configuration\n\n`train_chairs.py` and `train_sintel.py` train RAFT model via YAML configuration. Sample configs are in `configs` directory. Run;\n\n``` shell\n$ python train_chairs.py /path/to/config.yml\n```\n\n## Pre-trained models\n\nI made the pre-trained weights (on both FlyingChairs and MPI-Sintel) public.\nYou can download them via `gsutil` or `curl`.\n\n### Trained weights on FlyingChairs\n\n``` shell\n$ gsutil cp -r gs://tf-raft-pretrained/2020-09-26T18-38/checkpoints .\n```\nor\n``` shell\n$ mkdir checkpoints\n$ curl -OL https://storage.googleapis.com/tf-raft-pretrained/2020-09-26T18-38/checkpoints/model.data-00000-of-00001\n$ curl -OL https://storage.googleapis.com/tf-raft-pretrained/2020-09-26T18-38/checkpoints/model.index\n$ mv model* checkpoints/\n```\n\n### Trained weights on MPI-Sintel (Clean path)\n\n``` shell\n$ gsutil cp -r gs://tf-raft-pretrained/2020-09-26T08-51/checkpoints .\n```\nor\n``` shell\n$ mkdir checkpoints\n$ curl -OL https://storage.googleapis.com/tf-raft-pretrained/2020-09-26T08-51/checkpoints/model.data-00000-of-00001\n$ curl -OL https://storage.googleapis.com/tf-raft-pretrained/2020-09-26T08-51/checkpoints/model.index\n$ mv model* checkpoints/\n```\n\n### Load weights\n\n``` python\nraft = RAFT(iters=iters, iters_pred=iters_pred)\nraft.load_weights('checkpoints/model')\n\n# forward (with dummy inputs)\nx1 = np.random.uniform(0, 255, (1, 448, 512, 3)).astype(np.float32)\nx2 = np.random.uniform(0, 255, (1, 448, 512, 3)).astype(np.float32)\nflow_predictions = model([x1, x2], training=False)\n\nprint(flow_predictions[-1].shape) # >> (1, 448, 512, 2)\n```\n\n## Note\nThough I have tried to reproduce the original implementation faithfully, there is some difference between the original one and mine (mainly because of used framework: PyTorch/TensorFlow);\n\n- The original implementations provides cuda-based correlation function but I don't. My TF-based implementation works well, but cuda-based one may run faster.\n- I have trained my model on FlyingChairs and MPI-Sintel separately in my private environment (GCP with P100 accelerator). The model has been trained well, but not reached the best score reported in the paper (trained on multiple datasets).\n- The original one uses mixed-precision. This may get training much faster, but I don't. TensorFlow also enables mixed-precision with few additional lines, see https://www.tensorflow.org/guide/mixed_precision if interested.\n\nAdditional, global gradient clipping seems to be essential for stable training though it is not emphasized in the original paper. This operation can be done via `torch.nn.utils.clip_grad_norm_(model.parameters(), clip)` in PyTorch, `tf.clip_by_global_norm(grads, clip_norm)` in TF (coded at `self.train_step` in `tf_raft/model.py`).\n\n## References\n- https://github.com/princeton-vl/RAFT\n- https://github.com/NVIDIA/flownet2-pytorch\n- https://github.com/NVlabs/PWC-Net\n",
    'author': 'Daigo Hirooka',
    'author_email': 'daigo.hirooka@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/daigo0927/tf-raft',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
