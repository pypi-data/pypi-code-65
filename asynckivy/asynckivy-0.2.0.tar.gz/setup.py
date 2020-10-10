# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['asynckivy', 'asynckivy.adaptor']

package_data = \
{'': ['*']}

install_requires = \
['kivy>=1.11.1,<3.0.0']

setup_kwargs = {
    'name': 'asynckivy',
    'version': '0.2.0',
    'description': 'Async library for Kivy',
    'long_description': '# AsyncKivy\n\n[Youtube](https://youtu.be/rI-gjCsE1YQ)  \n[日本語doc](README_jp.md)  \n\n### Installation\n\n```\n# stable version\npip install asynckivy\n```\n\n```\n# development version\npip install git+https://github.com/gottadiveintopython/asynckivy.git@master#egg=asynckivy\n```\n\n### Usage\n\n```python\nimport asynckivy as ak\nfrom asynckivy.process_and_thread import \\\n    thread as ak_thread, process as ak_process\n\nasync def some_task(button):\n    # wait for 1sec\n    await ak.sleep(1)\n    \n    # wait until a button is pressed\n    await ak.event(button, \'on_press\')\n\n    # wait until \'button.x\' changes\n    __, x = await ak.event(button, \'x\')\n    print(f\'button.x is now {x}\')\n\n    # wait until \'button.x\' becomes greater than 100\n    if button.x <= 100:\n        __, x = await ak.event(button, \'x\', filter=lambda __, x: x>100)\n        print(f\'button.x is now {x}\')\n\n    # create a new thread, run a function on it, then\n    # wait for the completion of that thread\n    r = await ak_thread(some_heavy_task)\n    print(f"result of \'some_heavy_task()\': {r}")\n\n    # wait for the completion of subprocess\n    import subprocess\n    p = subprocess.Popen(...)\n    returncode = await ak_process(p)\n\n    # wait until EITHER a button is pressed OR 5sec passes\n    tasks = await ak.or_(\n        ak.event(button, \'on_press\'),\n        ak.sleep(5),\n    )\n    print("The button was pressed" if tasks[0].done else "5sec passed")\n\n    # wait until BOTH a button is pressed AND 5sec passes"\n    tasks = await ak.and_(\n        ak.event(button, \'on_press\'),\n        ak.sleep(5),\n    )\n\nak.start(some_task(some_button))\n```\n\n#### animation\n\n```python\nimport asynckivy as ak\n\nasync def some_task(widget):\n    # wait for the completion of an animation\n    await ak.animate(widget, width=200, t=\'in_out_quad\', d=.5)\n\n    # interpolate between the values 0 and 200\n    async for v in ak.interpolate(0, 200, s=.2, d=2, t=\'linear\'):\n        print(v)\n```\n\n#### touch handling\n\nYou can easily handle `on_touch_xxx` events via `asynckivy.rest_of_touch_moves()`.\n\n```python\nimport asynckivy as ak\n\nclass Painter(RelativeLayout):\n    def on_touch_down(self, touch):\n        if self.collide_point(*touch.opos):\n            ak.start(self.draw_rect(touch))\n            return True\n    \n    async def draw_rect(self, touch):\n        from kivy.graphics import Line, Color, Rectangle\n        from kivy.utils import get_random_color\n        with self.canvas:\n            Color(*get_random_color())\n            line = Line(width=2)\n        ox, oy = self.to_local(*touch.opos)\n        async for __ in ak.rest_of_touch_moves(self, touch):\n            # This part is iterated everytime \'on_touch_move\' is fired.\n            # Don\'t await anything during this iteration.\n            x, y = self.to_local(*touch.pos)\n            min_x = min(x, ox)\n            min_y = min(y, oy)\n            max_x = max(x, ox)\n            max_y = max(y, oy)\n            line.rectangle = [min_x, min_y, max_x - min_x, max_y - min_y]\n        # If you want to do something when \'on_touch_up\' is fired, do it here.\n        do_something_on_touch_up()\n```\n\n#### synchronization primitive\n\nThere is a Trio\'s [Event](https://trio.readthedocs.io/en/stable/reference-core.html#trio.Event) equivalent.\n\n```python\nimport asynckivy as ak\n\nasync def task_A(e):\n    print(\'A1\')\n    await e.wait()\n    print(\'A2\')\nasync def task_B(e):\n    print(\'B1\')\n    await e.wait()\n    print(\'B2\')\n\ne = ak.Event()\nak.start(task_A(e))\n# A1\nak.start(task_B(e))\n# B1\ne.set()\n# A2\n# B2\n```\n\n### planned api break in version 1.0.0\n\n- remove `animation()`, the older name of `animate()`\n- remove `all_touch_moves()`, the older name of `rest_of_touch_moves()`\n\n### Test Environment\n\n- CPython 3.7.1 + Kivy 1.11.1\n',
    'author': 'Nattōsai Mitō',
    'author_email': 'flow4re2c@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/gottadiveintopython/asynckivy',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
