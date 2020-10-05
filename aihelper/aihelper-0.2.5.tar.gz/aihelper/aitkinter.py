from tkinter import Toplevel, Label, Button, Frame, LEFT, W, Entry, TOP, X, RIGHT, YES, S, filedialog


class Popup:
    def __init__(self, parent, text):
        window = Toplevel(parent)
        label = Label(window, text=text)
        label.pack(fill="x", padx=50, pady=5)
        button_close = Button(window, text="Close", command=window.destroy)
        button_close.pack(fill="x")
        window.mainloop()


class EntryBar(Frame):
    def __init__(self, parent=None, picks=None, side=LEFT, anchor=W):
        Frame.__init__(self, parent)
        if picks is None:
            picks = []
        self.vars = []
        for pick in picks:
            row = Frame(parent)
            label = Label(row, width=10, text=pick, anchor=anchor)
            entry = Entry(row)
            row.pack(side=TOP, fill=X, padx=1, pady=1)
            label.pack(side=side)
            entry.pack(side=RIGHT, expand=YES, fill=X)
            self.vars.append((pick, entry))

    def state(self):
        return map(lambda var: (var[0], var[1].get()), self.vars)

    def get(self, string):
        return filter(
            None, map(lambda var: var[1].get() if string == var[0] else None, self.vars)
        )


class Browse(Frame):
    def __init__(self, parent=None, label=None, type='file', title='', initial=r'\\', anchor=S, side=LEFT):
        Frame.__init__(self, parent)
        self.file = ""
        if not label:
            self.label = Label(parent, font=("Helvetica", 9), fg="green")
        self.btn = Button(
            parent, text="Browse", command=lambda: self.browsefunc()
        ).pack(anchor=anchor, side=side)
        self.struct = {'file': filedialog.askopenfiles,
                       'dir': filedialog.askdirectory}
        self.type = type
        self.title = title
        self.initial = initial

    def browsefunc(self):
        if self.type =='file':
            mode = 'rb'
        else:
            mode = None
        self.file = self.struct[self.type](mode=mode, title=self.title, initial=self.initial)
        if self.type == 'file':
            self.label.config(text=self.file[0].name.split("/")[-1])
        else:
            self.label.config(text=self.file.split('/')[-1])
        self.label.pack()

    def get(self):
        return self.file


class OkButton(Frame):
    def __init__(
            self,
            parent=None,
            label=None,
            anchor=S,
            side=RIGHT,
            function=None,
            *args,
            **kwargs,
    ):
        Frame.__init__(self, parent)
        self.ok = Button(
            parent, text="Ok", command=lambda: function(*args, **kwargs)
        ).pack(anchor=anchor, side=side)
        self.label = label