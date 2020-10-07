#    _________             .__
#   /   _____/____    _____|  |__ _____
#   \_____  \\__  \  /  ___/  |  \\__  \
#   /        \/ __ \_\___ \|   Y  \/ __ \_
#  /_______  (____  /____  >___|  (____  /
#          \/     \/     \/     \/     \/
#    _________       _____  __
#   /   _____/ _____/ ____\/  |_
#   \_____  \ /  _ \   __\\   __\
#   /        (  <_> )  |   |  |
#  /_______  /\____/|__|   |__|
#          \/
#  Copyright (c) 2020.

"""
login module build gui
"""
from tkinter import Tk, Checkbutton, IntVar, Frame

from login_gui.frame import LoginFrame
from login_gui.user import User

__all__ = ['LoginGui', 'User', 'MainGui']


class LoginGui:
    """main window"""
    __root = None

    def __init__(self, root=None):
        if root is None or not isinstance(root, Tk):  # pragma: no cover
            self.root = Tk(className='Login')
            self.__center_window()
            LoginFrame(self.root)
            self.root.mainloop()
        else:
            LoginFrame(self.root)

    @property
    def root(self):
        """root Tk window"""
        return self.__root

    @root.setter
    def root(self, value):  # pragma: no cover
        if isinstance(value, Tk):
            self.__root = value
            return
        raise Exception('no Tk is value')

    def __center_window(self, wight=300, height=100):  # pragma: no cover
        """create standard issue"""
        # get screen width and height
        wight_screen = self.root.winfo_screenwidth()
        height_screen = self.root.winfo_screenheight()
        # calculate position x, y
        x = (wight_screen / 2) - (wight / 2)  # pylint: disable=invalid-name
        y = (height_screen / 2) - (height / 2)  # pylint: disable=invalid-name
        self.root.geometry('%dx%d+%d+%d' % (wight, height, x, y))


class MainGui:
    def __init__(self, functions, name='Login'):
        self.result = None
        if not isinstance(functions, list):
            raise IOError('functions must be list of names and function handler')
        wight = 300
        height = 100
        self.root = Tk(className=name)
        self._var = list()
        self._checkbox = list()
        for function in functions:
            if not isinstance(function, str):
                raise IOError('one function is a list names of function')
            self._var.append(IntVar())
            self._var[-1].set(1)
            self._checkbox.append(Checkbutton(self.root, text=function, variable=self._var[-1]))
            self._checkbox[-1].grid(columnspan=2)
        self.frame = Frame(self.root)
        self.frame.grid(columnspan=2)
        LoginFrame(self.frame, self)
        self.root.mainloop()

    def close(self):
        self.result = [x.get() for x in self._var]
        self.root.destroy()
