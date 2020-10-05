# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mujoco_maze']

package_data = \
{'': ['*'], 'mujoco_maze': ['assets/*']}

install_requires = \
['gym>=0.16', 'mujoco-py>=1.5']

entry_points = \
{'console_scripts': ['test = pytest:main']}

setup_kwargs = {
    'name': 'mujoco-maze',
    'version': '0.1.0',
    'description': 'Simple maze environments using mujoco-py',
    'long_description': '# mujoco-maze\n[![Actions Status](https://github.com/kngwyu/mujoco-maze/workflows/CI/badge.svg)](https://github.com/kngwyu/mujoco-maze/actions)\n[![Black](https://img.shields.io/badge/code%20style-black-000.svg)](https://github.com/psf/black)\n\nSome maze environments for reinforcement learning(RL) using [mujoco-py] and\n[openai gym][gym].\n\nThankfully, this project is based on the code from  [rllab] and [tensorflow/models][models].\n\n## Environments\n\n- PointUMaze/AntUmaze\n\n  ![PointUMaze](./screenshots/PointUMaze.png)\n  - PointUMaze-v0/AntUMaze-v0 (Distance-based Reward)\n  - PointUmaze-v1/AntUMaze-v1 (Goal-based Reward i.e., 1.0 or -ε)\n\n- Point4Rooms/Ant4Rooms\n\n  ![Point4Rooms](./screenshots/Point4Rooms.png)\n  - Point4Rooms-v0/Ant4Rooms-v0 (Distance-based Reward)\n  - Point4Rooms-v1/Ant4Rooms-v1 (Goal-based Reward)\n  - Point4Rooms-v2/Ant4Rooms-v2 (Multiple Goals (0.5 pt or 1.0 pt))\n\n- PointPush/AntPush\n\n  ![PointPush](./screenshots/AntPush.png)\n  - PointPush-v0/AntPush-v0 (Distance-based Reward)\n  - PointPush-v1/AntPush-v1 (Goal-based Reward)\n\n- PointFall/AntFall\n\n  ![PointFall](./screenshots/AntFall.png)\n  - PointFall-v0/AntFall-v0 (Distance-based Reward)\n  - PointFall-v1/AntFall-v1 (Goal-based Reward)\n\n- PointBilliard\n\n  ![PointBilliard](./screenshots/PointBilliard.png)\n  - PointBilliard-v0 (Distance-based Reward)\n  - PointBilliard-v1 (Goal-based Reward)\n  - PointBilliard-v2 (Multiple Goals (0.5 pt or 1.0 pt))\n\n## Warning\nThis project has some other environments (e.g., reacher, and swimmer)\nbut if they are not on README, they are work in progress and\nnot tested well.\n\n## License\nThis project is licensed under Apache License, Version 2.0\n([LICENSE-APACHE](LICENSE) or http://www.apache.org/licenses/LICENSE-2.0).\n\n[gym]: https://github.com/openai/gym\n[models]: https://github.com/tensorflow/models/tree/master/research/efficient-hrl\n[mujoco-py]: https://github.com/openai/mujoco-py\n[rllab]: https://github.com/rll/rllab\n',
    'author': 'Yuji Kanagawa',
    'author_email': 'yuji.kngw.80s.revive@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kngwyu/mujoco-maze',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
