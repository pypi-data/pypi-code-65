# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['trio_gtk']
install_requires = \
['pycairo<1.20', 'pygobject<3.32', 'trio>=0.17.0,<0.18.0']

setup_kwargs = {
    'name': 'trio-gtk',
    'version': '3.0.0',
    'description': 'Trio guest mode wrapper for PyGTK',
    'long_description': '# trio-gtk\n\n[![Build Status](https://drone.autonomic.zone/api/badges/decentral1se/trio-gtk/status.svg?ref=refs/heads/master)](https://drone.autonomic.zone/decentral1se/trio-gtk)\n\n## Trio guest mode wrapper for PyGTK\n\nUsing the [Trio guest mode](https://trio.readthedocs.io/en/latest/reference-lowlevel.html#using-guest-mode-to-run-trio-on-top-of-other-event-loops) feature, we can run both the Trio and PyGTK event loops alongside each other in a single program. This allows us to make use of the Trio library and the usual `async`/`await` syntax and not have to directly manage thread pools. This library provides a thin wrapper for initialising the guest mode and exposes a single public API function, `trio_gtk.run` into which you can pass your Trio main function.\n\n## Install\n\n```sh\n$ pip install trio-gtk\n```\n\nPlease note, `trio-gtk` does install [pygobject](https://gitlab.gnome.org/GNOME/pygobject) directly as a Python package. We use relaxed bounds to ensure that the hard dependency on system packages (see [cairo integration documentation](https://pygobject.readthedocs.io/en/latest/guide/cairo_integration.html) will not stop you having a successful installation. This may not always work out. If you see a build error during your Pip installation, please raise a ticket and we will see what we can do.\n\n## Example\n\n```python\nimport gi\nimport trio\n\ngi.require_version("Gtk", "3.0")\n\nfrom gi.repository import Gtk as gtk\n\nimport trio_gtk\n\n\nclass Example(gtk.Window):\n    def __init__(self, nursery):\n        gtk.Window.__init__(self, title="Example")\n\n        self.button = gtk.Button(label="Create a task")\n        self.button.connect("clicked", self.on_click)\n        self.add(self.button)\n\n        self.counter = 0\n        self.nursery = nursery\n\n        self.connect("destroy", gtk.main_quit)\n        self.show_all()\n\n    def on_click(self, widget):\n        self.counter += 1\n        self.nursery.start_soon(self.say_hi, self.counter)\n\n    async def say_hi(self, count):\n        while True:\n            await trio.sleep(1)\n            print(f"hi from task {count}")\n\n\nasync def main():\n    async with trio.open_nursery() as nursery:\n        Example(nursery)\n        await trio.sleep_forever()\n\n\ntrio_gtk.run(main)\n```\n',
    'author': 'decentral1se',
    'author_email': 'lukewm@riseup.net',
    'maintainer': 'decentral1se',
    'maintainer_email': 'lukewm@riseup.net',
    'url': 'https://github.com/decentral1se/trio-gtk',
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
