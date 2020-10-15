# Notebook tab specifying fits file object and drawing functions
# Derek Fujimoto
# Sept 2020

from tkinter import *
from tkinter import ttk, messagebox, filedialog

import os
import numpy as np
import pandas as pd

from bccd.backend.fits import fits
import bccd.backend.colors as colors
from bccd.backend.PltTracker import PltTracker as plt

from datetime import datetime
from dateutil import tz
from functools import partial

# =========================================================================== # 
class fits_tab(object):
    """
        Notebook tab specifying fits file object and drawing functions
        
        Data Fields:
            
            bccd: pointer to top level
            black: StringVar, black level
            entry_black: Entry widget for black value
            filename: name of .fits file
            id: id number for later deletion (key in bccd.tabs)
            input_names: dict, map input names to nice titles
            input_objs: dict of objects corresponding to input fields 
                             {input_name:(value,field,label)}
            img: fits image object
            old_alpha: int, last alpha draw value
            old_color: string, last color draw value
            plt: PltTracker obj, set to point at bccd.plt
            style: StringVar, drawing style
            styles: dict, map drawing style to draw function and input names
            tab_frame: tkk.Frame; top level frame for this tab
    """
    
    # (color, inverted)
    colours =  {'Greys':       True,
                'twilight':    True,
                'seismic':     False,
                'Reds':        True,
                'Blues':       True,
                'Greens':      True,
                'Purples':     True,
                'Oranges':     True,
                'viridis':     False,
                'plasma':      False,
                'inferno':     False,
                'magma':       False,
                'cividis':     False,
                'hot':         False,
                'afmhot':      False,
                'gist_heat':   False,
                'YlOrBr':      True,
                'YlOrRd':      True,
                'OrRd':        True,
                'PuRd':        True,
                'RdPu':        True,
                'BuPu':        True,
                'GnBu':        True,
                'PuBu':        True,
                'YlGnBu':      True,
                'PuBuGn':      True,
                'BuGn':        True,
                'YlGn':        True,  
                'binary':      True,
                'gist_yarg':   True,
                'gist_gray':   True,
                'gray':        False,
                'bone':        False,
                'pink':        False,
                'spring':      False,
                'summer':      False,
                'autumn':      False,
                'winter':      False,
                'cool':        True,
                'Wistia':      True,
                'copper':      False,
                'PiYG':        True,
                'PRGn':        True,
                'BrBG':        True,
                'PuOr':        True,
                'RdGy':        True,
                'RdBu':        True,
                'RdYlBu':      True,
                'RdYlGn':      True,
                'Spectral':    False,
                'coolwarm':    False,
                'bwr':         False,
                'twilight_shifted': False,
                'hsv':         True,
                }
    
    input_names = {'alpha':'Alpha (%): ',
                   'cmap':'Colour Map: ',
                   'nlevels':'Num. Contours: ',
                   'sigma':'Gaus. Filter Stdev.: ',
                   'imap':'Invert Colour Map'}
    
    # ======================================================================= #
    def __init__(self, bccd, tab_frame, filename, id):
        
        # inputs
        self.id = id
        self.bccd = bccd
        self.plt = bccd.plt
        self.tab_frame = tab_frame
        self.filename = filename
        self.old_color = tuple(self.colours.keys())[0]
        self.old_alpha = 100

        # read image
        img = fits(filename, plt=bccd.plt, rescale_pixels=bccd.rescale_pixels)
        self.img = img
        
        # variables
        self.black = StringVar()
        self.black.set(str(img.black))
        
        self.style = StringVar()
        
        # function, input names
        self.styles = { 'Greyscale':    (self.img.draw,'alpha','cmap','imap'),
                        'Contours':     (self.img.draw_contour,'alpha','nlevels','cmap','imap'),
                        'Gradient':     (self.img.draw_sobel,'alpha','cmap','imap'),
                        'Edges':        (self.img.draw_edges,'alpha','sigma','cmap','imap'),
                        }
                        
        # set draw style to previous
        if bccd.tabs:
            self.style.set(bccd.tabs[-1].style.get())
        else:
            self.style.set(list(self.styles.keys())[0])
        
        self.input_objs = {}
       
        # Column 0 -----------------------------------------------------------
        r = 0
        
        frame_column0 = ttk.Frame(tab_frame, relief='sunken',pad=5)
        frame_column0.grid(column=0,row=0,rowspan=10,sticky=(N,W),padx=5,pady=5)
        
        # show main title and exposure
        ttk.Label(frame_column0,
                  text=os.path.basename(filename)).grid(column=0,row=r,sticky=W); r+=1
        ttk.Label(frame_column0,
                  text='Exposure: %.3f s'%img.header['EXPOSURE']).grid(column=0,row=r,sticky=W); r+=1
        
        # show date and time, converted from utc to local
        date = img.header['DATE-OBS']
        from_zone = tz.tzutc()
        to_zone = tz.gettz('Canada/Vancover')
        
        utc = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')
        utc = utc.replace(tzinfo=from_zone)
        local = utc.astimezone(to_zone)
        
        date = local.strftime("%Y-%m-%d")
        time = local.strftime("%H:%M:%S")
        
        ttk.Label(frame_column0,text=date).grid(column=0,row=r,sticky=W); r+=1
        ttk.Label(frame_column0,text=time).grid(column=0,row=r,sticky=W); r+=1
        
        # Columnn 1 -----------------------------------------------------
        
        frame_column1 = ttk.Frame(tab_frame, relief='sunken',pad=5)
        frame_column1.grid(column=1,row=0,rowspan=10,sticky=(N,W),padx=5,pady=5)
        
        label_style = ttk.Label(frame_column1, text='Draw Style: ')
        combo_style = ttk.Combobox(frame_column1, textvariable=self.style, 
                                   state='readonly', width=20)
        combo_style['values'] = tuple(self.styles.keys())
        
        r = 0
        label_style.grid(column=0,row=r,sticky=W)
        combo_style.grid(column=1,row=r,sticky=W); r+=1
        
        # black level
        label_black = ttk.Label(frame_column1,text='Black Value: ')
        frame_black = ttk.Frame(frame_column1)
        self.entry_black = ttk.Entry(frame_black, textvariable=self.black, width=10)
        button_black = ttk.Button(frame_black, text='Reset', width=8, 
                                  command=self.reset_black)
        
        label_black.grid(column=0,row=r,sticky=W)
        frame_black.grid(column=1,row=r,sticky=W); r+=1
        self.entry_black.grid(column=0,row=0,sticky=W)
        button_black.grid(column=1,row=0,sticky=W, padx=2)
        
        # Inputs for draw style
        combo_style.bind("<<ComboboxSelected>>", 
                         partial(self.change_draw_fn, frame=frame_column1, row=r))
        r = self.input_place(frame_column1,r)+1
        
        # Draw buttons
        frame_draw = ttk.Frame(frame_column1)
        button_remove = ttk.Button(frame_draw,text='Remove',command=self.remove)
        button_draw_super = ttk.Button(frame_draw,text='Superimpose',command=self.draw)
        button_draw_new = ttk.Button(frame_draw,text='Draw New',command=self.draw_new)
        
    
        frame_draw.grid(column=0,row=r,sticky=(W,E,N),columnspan=2); r+=1
        frame_draw.columnconfigure(1,weight=1)
        c = 0
        button_remove.grid(column=c,row=0,sticky=W); c+=2
        button_draw_super.grid(column=c,row=0,sticky=E); c+=1
        button_draw_new.grid(column=c,row=0,sticky=E); c+=1
                
        button_close = ttk.Button(tab_frame,text='x',command=self.close, pad=0, 
                                  width=3)
        button_close.grid(column=10,row=0,sticky=(N,E),pady=5)
        
        # resizing
        tab_frame.grid_columnconfigure(9, weight=1)        # main area
        tab_frame.grid_rowconfigure(9,weight=1)            # main area
    
    # ======================================================================= #
    def close(self):
        """Remove the tab"""
        
        selected = self.bccd.notebook.select()
        self.bccd.notebook.forget(selected)
        self.tab_frame.destroy()
        
        for item in self.bccd.notebook.winfo_children():
            if str(item)==selected:
                item.destroy()       
                break
        
        for i,tab in enumerate(self.bccd.tabs):
            if tab is self:
                del self.bccd.tabs[i]
                break
    
    # ======================================================================= #
    def change_draw_fn(self, event, frame, row):
        """Change the draw function"""
        self.input_remove()
        self.input_place(frame, row)
    
    # ======================================================================= #
    def draw(self):
        """
            Draw image based on selection
        """
        
        # get draw style
        style = self.style.get()
        
        # get draw fn
        fn = self.styles[style][0]
        
        # set black level 
        self.img.set_black(float(self.black.get()))
        
        # get inputs
        options = {}
        
        for k,v in self.input_objs.items():
            if k in ('sigma',):
                options[k] = float(v[0].get())
            elif k == 'alpha':
                options[k] = v[0].get()/100
            else:
                options[k] = v[0].get()
        
        # draw
        fn(**options)
    
    # ======================================================================= #
    def draw_new(self):
        """
            Draw in a new window
        """
        self.plt.figure()
        self.draw()
        
    # ======================================================================= #
    def input_place(self, frame, row):
        """
            Create and grid new input fields
            
            frame:  ttk.Frame obj to draw in
            row:    starting row. Assume starting column is 0
            
            returns: final row
            adds items to self.input_objs
        """
        
        # setup
        style = self.style.get()
        input_names = self.styles[style][1:]
        
        # make objects
        for inpt in input_names:
            
            # alpha
            if inpt == 'alpha':
                
                # make elements
                label = ttk.Label(frame, text=self.input_names[inpt])
                value = IntVar()
                element = Spinbox(frame, textvariable=value, width=5, from_=0, to=100)
                value.set(self.old_alpha)
                
            # colour map
            elif inpt == 'cmap':
                
                # make elements
                label = ttk.Label(frame, text=self.input_names[inpt])
                value = StringVar()
                element = ttk.Combobox(frame, textvariable=value, 
                                       state='readonly', width=20)
                element.bind("<<ComboboxSelected>>", self.set_imap)
                element['values'] = tuple(self.colours.keys())
                value.set(self.old_color)
                
            # number contours
            elif inpt == 'nlevels':
                
                # make elements
                label = ttk.Label(frame, text=self.input_names[inpt])
                value = IntVar()
                element = Spinbox(frame, textvariable=value, width=5, from_=1, 
                                  to=1000)
                value.set(5)
                
            # invert colour map
            elif inpt == 'imap':
                
                # make elements
                label = ttk.Label(frame, text='')
                value = BooleanVar()
                element = ttk.Checkbutton(frame, text=self.input_names[inpt],
                        variable=value, onvalue=False, offvalue=True,
                        pad=5)
                value.set(self.colours[self.input_objs['cmap'][0].get()])
                
            # gaussian filter radius
            elif inpt == 'sigma':
                
                # make elements
                label = ttk.Label(frame, text=self.input_names[inpt])
                value = StringVar()
                element = ttk.Entry(frame, textvariable=value, width=10)
                element.insert(0,"1")
                
            else:
                raise RuntimeError('Input %s not implemented' % inpt)
                
            # grid
            label.grid(column=0, row=row, sticky=(N,W))
            element.grid(column=1, row=row, sticky=(N,W))
            
            # save 
            self.input_objs[inpt] = (value, element, label)
            
            # incrment the gridding row
            row += 1
                
        return row
        
    # ======================================================================= #
    def input_remove(self):
        """Remove draw function options"""
        
        self.old_color = self.input_objs['cmap'][0].get()
        
        try:
            self.old_alpha = self.input_objs['alpha'][0].get()
        except KeyError:
            pass
        
        for k,i in self.input_objs.items():
            i[1].grid_forget()
            i[2].grid_forget()
            i[1].update_idletasks()
            i[2].update_idletasks()
        
        keys = tuple(self.input_objs.keys())
        for k in keys:
            del self.input_objs[k]
            
        self.input_objs = {}
        
        
    # ======================================================================= #
    def remove(self):
        """
            Remove image from the active figure
        """
        self.plt._remove_drawn_object(self.plt.gca(),self.filename)
    
    # ======================================================================= #
    def reset_black(self):
        """
            Reset black to header value
        """
        black = self.img.header['BZERO']
        self.entry_black.delete(0,END)
        self.entry_black.insert(0,str(black))
        self.black.set(str(black))
        
    # ======================================================================= #
    def set_imap(self, *args):
        """
            Set imap based on color seclection
        """
        
        imap = self.input_objs['imap'][0]
        cmap = self.input_objs['cmap'][0]
        imap.set(self.colours[cmap.get()])
