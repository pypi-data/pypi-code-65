# Popup to set target settings
# Derek Fujimoto
# Sep 2020

from tkinter import *
from tkinter import ttk
import textwrap

from bccd.backend import colors
from bccd.backend.Target import Circle, Square, Rectangle


# ========================================================================== #
class popup_target(object):
    """
        Popup window for setting targeting options. 
        
        Data fields: 
            ax_list: list of axes on which the current target is drawn
            color: string. matplotlib color 
            frame_color: tk frame for showing the color of the target lines
            radios: list of radio buttons
            result_label: ttk.label object for showing target info
            shape: StringVar, stores shape to draw
            target: Target object
            win: toplevel window
    """

    description = '\n'.join(textwrap.wrap("Draw a shape in the active figure, "+\
                                "synchronized across multiple figures.",width=30))
                    
    # colours in the default matplotlib cycle
    colors = {  'C0':'#1f77b4',
                'C1':'#ff7f0e', 
                'C2':'#2ca02c', 
                'C3':'#d62728',
                'C4':'#9467bd',
                'C5':'#8c564b', 
                'C6':'#e377c2',
                'C7':'#7f7f7f',
                'C8':'#bcbd22',
                'C9':'#17becf',
                }
                
    shapes = ('circle','square','rectangle')

    # ====================================================================== #
    def __init__(self, bccd, color='C0'):
        self.bccd = bccd
        self.color = color
        self.ax_list = []
        
        # make a new window
        win = Toplevel(bccd.mainframe)
        win.title('Set and Draw Target')
        
        # target
        self.target = None
        
        # icon
        bccd.set_icon(win)
        
        # Key bindings
        win.bind('<Return>',self.draw)             
        win.bind('<KP_Enter>',self.draw)
    
        win.protocol("WM_DELETE_WINDOW", self.on_closing)
    
        # Column0 ----------------------------------------------------------
        frame_col0 = ttk.Frame(win, relief='sunken', pad=5)
        frame_col0.grid(column=0, row=0, sticky=(N,S,E,W), padx=5, pady=5)
    
        # Colour swatch
        self.frame_color = Frame(frame_col0, width=200, height=30)
        self.frame_color.grid(column=0,row=0,sticky=(N,W,S,E), padx=10, pady=10)
        self.frame_color.columnconfigure(0,weight=1)
        self.frame_color.rowconfigure(0,weight=1)
        self.set_frame_color(self.colors[self.color])
        
        # Header
        ttk.Label(frame_col0, text=self.description).grid(column=0, row=1,
                  sticky=(N,W), padx=10, pady=10)
        
        # target info label
        self.result_label = ttk.Label(frame_col0, text='')
        self.result_label.grid(column=0, row=2, sticky=(N,W), padx=10, pady=10)
        
        # Column1 ----------------------------------------------------------
        frame_col1 = ttk.Frame(win, relief='sunken', pad=5)
        frame_col1.grid(column=1, row=0, sticky=(N,S,E,W), padx=5, pady=5)
        
        # draw shape radio buttons
        self.shape = StringVar()
        self.radios = []
        for i,v in enumerate(self.shapes):
            rad = ttk.Radiobutton(frame_col1, 
                            text=v.title().rjust(max([len(s) for s in self.shapes])), 
                            variable=self.shape, 
                            value=v)
            rad.grid(column=0, row=i, sticky=(N,W))
            self.radios.append(rad)
            frame_col1.rowconfigure(i,weight=1)
            
        self.shape.set(self.shapes[0])
        
        # Row2 ----------------------------------------------------------
        
        frame_row2 = ttk.Frame(win, relief='sunken', pad=5)
        frame_row2.grid(column=0, row=1, sticky=(N,S,E,W), padx=5, pady=5, columnspan=2)
        frame_row2.columnconfigure(0,weight=1)
        frame_row2.columnconfigure(1,weight=1)
        
        # buttons
        button_draw = ttk.Button(frame_row2, text='Draw', command=self.draw)
        button_remove = ttk.Button(frame_row2, text='Remove', command=self.remove)
        
        button_draw.grid(column=1,   row=0, sticky=(N,E,W,S))
        button_remove.grid(column=0, row=0, sticky=(N,E,W,S))
        
        self.win = win
        
    # ====================================================================== #
    def draw(self,*args):
        """
            Add the target to the open figure
            Disable the radio buttons
            Create the target object
        """
        
        # disable the radio buttons
        for r in self.radios:
            r.config(state='disabled')
        
        if self.target is None:
            if self.shape.get() == 'circle':
                self.target = Circle(self, self.color, self.result_label, 250, 185, 50)  
            elif self.shape.get() == 'square':
                self.target = Square(self, self.color, self.result_label, 250, 185, 50)  
            elif self.shape.get() == 'rectangle':
                self.target = Rectangle(self, self.color, self.result_label, 250, 185, 50)  
            else: 
                raise RuntimeError("Undefined shape")
        
        self.target.draw(self.bccd.plt.gca())
    
    # ====================================================================== #
    def remove(self):
        """
            Remove the target from the open figure
        """
        self.target.remove(ax=self.bccd.plt.gca())
        
    # ====================================================================== #
    def set_frame_color(self, color='#FFFFFF'):
        """
            Set the color frame color
        """
        
        if color in self.colors.keys():
            self.frame_color.config(bg=self.colors[color])
        else:
            self.frame_color.config(bg=color)
    
    # ====================================================================== #
    def on_closing(self):
        try:
            self.target.remove_all()
        except AttributeError:
            pass
            
        self.bccd.targets.remove(self)
        self.win.destroy()
