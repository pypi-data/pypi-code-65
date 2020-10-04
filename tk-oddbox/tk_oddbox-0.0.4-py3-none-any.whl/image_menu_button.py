from typing import List
from tkinter import Menu, Menubutton, StringVar, Widget
from functools import partial

from tk_oddbox.images import Images


class ImageMenuButton(Menubutton):
    def __init__(
        self, parent: Widget, string_var: StringVar, names: List[str], *args, **kwargs
    ):
        """Parent widget and string var are required.

        Args:
            parent: parent frame menubutton belongs to
            string_var: must be set a name in Images.
            names: all must be names of Images to select from.
        """
        Menubutton.__init__(self, parent, *args, **kwargs)
        self.__string_var = string_var
        self.__string_var.trace("w", self.__trace_callback)
        value = string_var.get()
        self.config(image=Images[value])
        menu = Menu(self)
        self["menu"] = menu
        for name in names:
            image = Images[name]
            callback = partial(self.__select_callback, name)
            menu.add_command(image=image, command=callback)

    def __select_callback(self, name: str):
        self.__string_var.set(name)

    def __trace_callback(self, *ignored):
        name = self.__string_var.get()
        self.config(image=Images[name])
