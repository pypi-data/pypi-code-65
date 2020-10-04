from tkinter import Label, StringVar, Widget

from tk_oddbox.images import Images


class ImageLabel(Label):
    def __init__(self, parent: Widget, string_var: StringVar, *args, **kwargs):
        """Parent widget and string var are required.

        Args:
            parent: parent frame menubutton belongs to
            string_var: must be set a name in Images.
        """
        Label.__init__(self, parent, *args, **kwargs)
        self.__string_var = string_var
        self.__string_var.trace("w", self.__trace_callback)
        name = string_var.get()
        self.config(image=Images[name])

    def __trace_callback(self, *ignored):
        name = self.__string_var.get()
        self.config(image=Images[name])
