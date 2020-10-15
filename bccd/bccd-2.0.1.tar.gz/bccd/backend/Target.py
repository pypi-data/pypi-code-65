# Target for targeting
# Derek Fujimoto
# Sep 2020 

import matplotlib.patches as patches
from functools import partial

class Target(object):
    
    """
        Drawing shapes on lots of figures
        
        Data fields:
            ax_list: list of axis
            bccd: bccd object
            color: string, maplotlib color name for coloring everything
            figures: list of figures to update
            label: ttk label object to update text on properties
            popup_target: popup_target object
            points: list of all DraggablePoints
            
    """

    # ======================================================================= #
    def __init__(self, popup_target, color, label):
        
        self.bccd = popup_target.bccd 
        self.popup_target = popup_target 
        self.ax_list = []
        self.color = color
        self.label = label
        self.points = []
        
    # ======================================================================= #
    def draw(self, ax):
        """
            Axis operations for drawing
        """
        # check if already drawin in these axes
        if ax in self.ax_list:
            raise RuntimeError("Axis already contains this target") 
                
        # connect with window close
        ax.figure.canvas.mpl_connect('close_event', partial(self.remove,ax=ax))
                
        # add axes to list
        self.ax_list.append(ax)
        
    # ======================================================================= #
    def remove(self, *args, ax=None):
        """
            Remove the DraggablePoints and patch from the axis
        """
        if ax not in self.ax_list:
            return
                
        # remove points 
        for pt in self.points:     
            pt.remove(ax)
            
        # remove patches
        for patch in ax.patches:
            if patch in self.patches:
                ax.patches.remove(patch)
                self.patches.remove(patch)
        
        # remove axis from list
        self.ax_list.remove(ax)
        
    # ======================================================================= #
    def remove_all(self):
        """
            Remove the DraggablePoints and patch from all axes
        """
        for ax in self.ax_list.copy():
            self.remove(ax=ax)
            
class Circle(Target):
    """
        Drawing circle target shapes on lots of figures
        
        Data fields:
            pt_center, pt_radius: DraggablePoints
            patches: mpl.patches for patches
            x,y: center coordinates
            r: radius
    """

    # ======================================================================= #
    def __init__(self, popup_target, color, label, x, y, r):
        
        super().__init__(popup_target, color, label)
        
        # save circle position
        self.x = x
        self.y = y
        self.r = r
        
        # place circle at the center of the window
        self.patches = []
        
        # center
        self.pt_center = DraggablePoint(self,self.update_center,
                            setx=True,sety=True,color=self.color, marker='x')
        
        # radius
        self.pt_radius = DraggablePoint(self,self.update_radius,
                            setx=True,sety=False,color=self.color, marker='o')
        
        self.points = [self.pt_center, self.pt_radius]
        self.update_popup_label()
        
    # ======================================================================= #
    def draw(self, ax):
        """Add the target to the current axes"""
        
        super().draw(ax)
        
        # draw things
        self.patches.append(patches.Circle((self.x,self.y),self.r,
                                     fill=False, 
                                     facecolor='none',
                                     lw=1,
                                     ls='-',
                                     edgecolor=self.color))
        ax.add_patch(self.patches[-1])
        self.pt_center.add_ax(ax, self.x, self.y)
        self.pt_radius.add_ax(ax, self.x+self.r, self.y,)

    # ======================================================================= #
    def update_popup_label(self):
        """Update popup window label with info on target"""
        
        self.label.config(text='x = %d\ny = %d\nr = %d' % (self.x, self.y, self.r))
        
    # ======================================================================= #
    def update_center(self, x, y):
        """
            Update circle position based on DraggablePoint
        """
        self.pt_radius.set_xdata(x+self.r)
        self.pt_radius.set_ydata(y)
        
        for c in self.patches:
            c.set_center((x,y))
        
        self.x = x
        self.y = y
        self.update_popup_label()
    
    # ======================================================================= #
    def update_radius(self, x, y):
        """
            Update circle radius based on DraggablePoint
        """

        self.r = abs(self.x-x)
        
        for c in self.patches:
            c.set_radius(self.r)
            
        self.update_popup_label()
    
class Square(Target):
    """
        Drawing square target shapes on lots of figures
        
        Data fields:
            pt_center, pt_side: DraggablePoints
            square: mpl.patches for patches
            x,y: center coordinates
            side: side length
    """

    # ======================================================================= #
    def __init__(self, popup_target, color, label, x, y, side):
        
        super().__init__(popup_target, color, label)
        
        # save circle position
        self.x = x
        self.y = y
        self.side = side
        
        # place circle at the center of the window
        self.patches = []
        
        # center
        self.pt_center = DraggablePoint(self,self.update_center,
                            setx=True,sety=True,color=self.color, marker='x')
        
        # radius
        self.pt_side = DraggablePoint(self,self.update_side,
                            setx=True,sety=False,color=self.color, marker='s')
        
        self.points = [self.pt_center, self.pt_side]
        self.update_popup_label()
        
    # ======================================================================= #
    def draw(self, ax):
        """Add the target to the current axes"""
        
        super().draw(ax)
        
        # draw things
        self.patches.append(patches.Rectangle((self.x-self.side,self.y-self.side),
                                            width=self.side*2,
                                            height=self.side*2,
                                            fill=False, 
                                            facecolor='none',
                                            lw=1,
                                            ls='-',
                                            edgecolor=self.color))
        ax.add_patch(self.patches[-1])
        self.pt_center.add_ax(ax, self.x, self.y)
        self.pt_side.add_ax(ax, self.x+self.side, self.y)

    # ======================================================================= #
    def update_popup_label(self):
        """Update popup window label with info on target"""
        
        self.label.config(text='x = %d\ny = %d\nside = %d' % (self.x, self.y, self.side*2))
        
    # ======================================================================= #
    def update_center(self, x, y):
        """
            Update circle position based on DraggablePoint
        """
        self.pt_side.set_xdata(x+self.side)
        self.pt_side.set_ydata(y)
        
        for c in self.patches:
            c.set_xy((x-self.side,y-self.side))
        
        self.x = x
        self.y = y
        self.update_popup_label()
    
    # ======================================================================= #
    def update_side(self, x, y):
        """
            Update circle radius based on DraggablePoint
        """

        self.side = abs(self.x-x)
        dx = self.side*2
        
        for c in self.patches:
            c.set_xy((self.x-self.side,self.y-self.side))
            c.set_height(dx)
            c.set_width(dx)
            
        self.update_popup_label()
        
class Rectangle(Target):
    """
        Drawing Rectangle target shapes on lots of figures
        
        Data fields:
            pt_tr, pt_tl, pt_br, pt_bl: DraggablePoints
            patches:    mpl.patches for patches
            x,y:    center coordinates
            dx,dy:  side length
    """

    # ======================================================================= #
    def __init__(self, popup_target, color, label, x, y, side):
        
        super().__init__(popup_target, color, label)
        
        # save circle position
        self.x = x
        self.y = y
        self.dx = side
        self.dy = side
        
        # place circle at the center of the window
        self.patches = []
        
        # corner points (tr = top right)
        self.pt_tl = DraggablePoint(self,self.update_tl,
                            setx=True,sety=True,color=self.color, marker='s')
        
        self.pt_tr = DraggablePoint(self,self.update_tr,
                            setx=True,sety=True,color=self.color, marker='s')

        self.pt_br = DraggablePoint(self,self.update_br,
                            setx=True,sety=True,color=self.color, marker='s')

        self.pt_bl = DraggablePoint(self,self.update_bl,
                            setx=True,sety=True,color=self.color, marker='s')
        
        self.points = [self.pt_tl, self.pt_tr, self.pt_br, self.pt_bl]
        self.update_popup_label()
        
    # ======================================================================= #
    def draw(self, ax):
        """Add the target to the current axes"""
        
        super().draw(ax)
        
        # draw things
        self.patches.append(patches.Rectangle((self.x-self.dx,self.y-self.dy),
                                            width=self.dx*2,
                                            height=self.dy*2,
                                            fill=False, 
                                            facecolor='none',
                                            lw=1,
                                            ls='-',
                                            edgecolor=self.color))
        ax.add_patch(self.patches[-1])
        self.pt_tr.add_ax(ax, self.x+self.dx, self.y+self.dy)
        self.pt_tl.add_ax(ax, self.x-self.dx, self.y+self.dy)
        self.pt_br.add_ax(ax, self.x+self.dx, self.y-self.dy)
        self.pt_bl.add_ax(ax, self.x-self.dx, self.y-self.dy)
        
    # ======================================================================= #
    def update_popup_label(self):
        """Update popup window label with info on target"""
        
        self.label.config(text='x = %d\ny = %d\ndx = %d\ndy = %d' % \
                (self.x, self.y, self.dx*2, self.dy*2))
        
    # ======================================================================= #
    def update_tr(self, x, y):
        """
            Update top right position based on DraggablePoint
        """
        self.pt_tl.set_ydata(y)
        self.pt_br.set_xdata(x)
        
        ddx = x - int(self.pt_tl.get_xdata())
        ddy = y - int(self.pt_br.get_ydata())
        
        dx = round(ddx/2)
        dy = round(ddy/2)
        
        for c in self.patches:
            c.set_xy((x-ddx,y-ddy))
            c.set_width(ddx)
            c.set_height(ddy)
        
        self.x = x-dx
        self.y = y-dy
        
        self.dx = abs(dx)
        self.dy = abs(dy)
        
        self.update_popup_label()
    
    # ======================================================================= #
    def update_tl(self, x, y):
        """
            Update top left position based on DraggablePoint
        """
        self.pt_tr.set_ydata(y)
        self.pt_bl.set_xdata(x)
        
        ddx = int(self.pt_tr.get_xdata()) - x
        ddy = y- int(self.pt_bl.get_ydata())
        
        dx = round(ddx/2)
        dy = round(ddy/2)
        
        for c in self.patches:
            c.set_xy((x,y-ddy))
            c.set_width(ddx)
            c.set_height(ddy)
        
        self.x = x+dx
        self.y = y-dy
        
        self.dx = abs(dx)
        self.dy = abs(dy)
        
        self.update_popup_label()
        
    # ======================================================================= #
    def update_br(self, x, y):
        """
            Update bottom right position based on DraggablePoint
        """
        self.pt_bl.set_ydata(y)
        self.pt_tr.set_xdata(x)
        
        ddx = x - int(self.pt_bl.get_xdata())
        ddy = int(self.pt_tr.get_ydata()) - y
        
        dx = round(ddx/2)
        dy = round(ddy/2)
        
        for c in self.patches:
            c.set_xy((x-ddx,y))
            c.set_width(ddx)
            c.set_height(ddy)
        
        self.x = x-dx
        self.y = y+dy
        
        self.dx = abs(dx)
        self.dy = abs(dy)
        
        self.update_popup_label()
        
    # ======================================================================= #
    def update_bl(self, x, y):
        """
            Update bottom left position based on DraggablePoint
        """
        self.pt_br.set_ydata(y)
        self.pt_tl.set_xdata(x)
        
        ddx = int((self.pt_br.get_xdata() - x))
        ddy = int((self.pt_tl.get_ydata() - y))
        
        dx = round(ddx/2)
        dy = round(ddy/2)
        
        for c in self.patches:
            c.set_xy((x,y))
            c.set_width(ddx)
            c.set_height(ddy)
        
        self.x = x+dx
        self.y = y+dy
        
        self.dx = abs(dx)
        self.dy = abs(dy)
        
        self.update_popup_label()
                
class DraggablePoint:

    # http://stackoverflow.com/questions/21654008/matplotlib-drag-overlapping-points-interactively
    # https://stackoverflow.com/questions/28001655/draggable-line-with-draggable-points
    
    lock = None #  only one can be animated at a time
    size=8

    # ======================================================================= #
    def __init__(self,parent,updatefn,setx=True,sety=True,color=None, marker='s'):
        """
            parent: parent object
            points: list of point objects, corresponding to the various axes 
                    the target is drawn in 
            updatefn: funtion which updates the line in the corpatchest way
                updatefn(xdata,ydata)
            x,y: initial point position
            setx,sety: if true, allow setting this parameter
            color: point color
        """
        self.parent = parent
        self.points = []
        self.color = color
        self.marker = marker
            
        self.updatefn = updatefn
        self.setx = setx
        self.sety = sety
        self.press = None
        self.background = None
        
        # trackers for connections
        self.cidpress = []
        self.cidrelease = []
        self.cidmotion = []
        
    # ======================================================================= #
    def add_ax(self, ax, x=None, y=None):
        """Add axis to list of axes"""
        
        self.disconnect()
        
        if x is None:
            x = self.get_xdata()
        if y is None:
            y = self.get_ydata()
            
        self.points.append(ax.plot(x, y, zorder=100, color=self.color, alpha=0.5, 
                        marker=self.marker, markersize=self.size)[0])
        self.points[-1].set_pickradius(self.size)
        
        self.connect()
        
    # ======================================================================= #
    def connect(self):
        """connect to all the events we need"""
        
        # trackers for connections
        self.cidpress = []
        self.cidrelease = []
        self.cidmotion = []
        
        for i,pt in enumerate(self.points):
            self.cidpress.append(pt.figure.canvas.mpl_connect('button_press_event', 
                                partial(self.on_press, id=i)))
                                 
            self.cidrelease.append(pt.figure.canvas.mpl_connect('button_release_event', 
                                self.on_release))
                                
            self.cidmotion.append(pt.figure.canvas.mpl_connect('motion_notify_event', 
                                partial(self.on_motion, id=i)))
    
    # ======================================================================= #
    def on_press(self, event, id):
        
        if event.inaxes != self.points[id].axes: return
        if DraggablePoint.lock is not None: return
        contains, attrd = self.points[id].contains(event)
        if not contains: return
        DraggablePoint.lock = self
        
    # ======================================================================= #
    def on_motion(self, event, id):

        if DraggablePoint.lock is not self: return
        if event.inaxes != self.points[id].axes: return
        
        # get data
        x = event.xdata
        y = event.ydata
        
        # move the point
        if self.setx:   self.set_xdata(x)
        if self.sety:   self.set_ydata(y)

        # update the line
        self.updatefn(x,y)        

    # ======================================================================= #
    def on_release(self, event):
        'on release we reset the press data'
        if DraggablePoint.lock is not self: return
        DraggablePoint.lock = None
        
    # ======================================================================= #
    def disconnect(self):
        'disconnect all the stored connection ids'
        
        for i,pt in enumerate(self.points):
            pt.figure.canvas.mpl_disconnect(self.cidpress[i])
            pt.figure.canvas.mpl_disconnect(self.cidrelease[i])
            pt.figure.canvas.mpl_disconnect(self.cidmotion[i])
                
    # ======================================================================= #
    def get_xdata(self):
        """Get x coordinate"""
        return self.points[0].get_xdata()
            
    # ======================================================================= #
    def get_ydata(self):
        """Get y coordinate"""
        return self.points[0].get_ydata()
            
    # ======================================================================= #
    def remove(self, ax):
        """
            Remove drawn points from the axis.
        """
    
        self.disconnect()
        del_list = []
        
        # remove from draggable points
        for i,line in enumerate(ax.lines):
            for pt in self.points:
                if line is pt:
                    del_list.append(i)
                    self.points.remove(line)
                    del line
        
        # remove from mpl
        for d in del_list:
            ax.lines[d].remove()
        
        self.connect()
            
    # ======================================================================= #
    def set_xdata(self, x):
        """Set x coordinate"""
        for pt in self.points:
            pt.set_xdata(x)    
            
    # ======================================================================= #
    def set_ydata(self, y):
        """Set y coordinate"""
        for pt in self.points:
            pt.set_ydata(y)
