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
login frame for gui
"""
from tkinter import Frame, Label, Entry, IntVar, Checkbutton, Button, NORMAL, DISABLED, E, Tk

from login_gui.loader import Loader
from login_gui.user import User

HEIGHT = 1
WIDTH = 17


class LoginFrame(Frame):  # pylint: disable=too-many-ancestors
    """build frame for gui"""

    def __init__(self, master, main=None):
        super().__init__(master)
        self.main = main
        self._label_username = Label(self, text="Username")
        self._label_password = Label(self, text="Password")

        self._entry_username = Entry(self)
        self._entry_password = Entry(self, show="*")

        self._label_username.grid(row=0, sticky=E)
        self._label_password.grid(row=1, sticky=E)
        self._entry_username.grid(row=0, column=1)
        self._entry_password.grid(row=1, column=1)

        self._var = IntVar()
        self._var.set(1)
        self._checkbox = Checkbutton(self, text="Save login data (64-bit)", variable=self._var)

        self._checkbox.grid(columnspan=2)

        self._loader = Loader()

        self._login_button = Button(self, text="login", command=self.__login_click, height=HEIGHT, width=WIDTH)
        self._load_button = Button(self, text="Load from " + self._loader.last_date, command=self._close,
                                   height=HEIGHT,
                                   width=WIDTH)
        self._login_button.config(state=NORMAL)

        self._load_button.config(state=DISABLED)
        if self._loader.is_exist:  # pragma: no cover
            self._load_button.config(state=NORMAL)

        self._login_button.grid(row=3, column=0)
        self._load_button.grid(row=3, column=1)

        self.pack()

    def __login_click(self):
        User().user64 = '{}:{}'.format(self._entry_username.get(), self._entry_password.get())
        if self._var.get():  # pragma: no cover
            self._loader.write(User().user64)
        self._close()

    def _close(self):
        self.master.destroy()
        if self.main is not None:
            self.main.close()
