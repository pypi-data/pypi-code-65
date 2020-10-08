'''module for making window arrays on exterior walls'''
import math

def make_louvers(wl_name, 
                 wl_width,
                 wn_width, 
                 wn_height, 
                 wn_offset,
                 l_fin_depth, 
                 r_fin_depth, 
                 hang_depth, 
                 gl_type,
                 x_start):
    '''takes some arguments (all mandatory for now,
    prints input-file-ready syntax and also returns a list of
    input-ready syntax for each window.'''
    
    x_offset = wn_width + wn_offset
    x_offset = wn_offset    

    num_win = math.floor((wl_width-x_start) / (wn_width + x_offset))
    x = x_start
    winlist = []
    for win in range(num_win):
        wn_name = wl_name + "_array_win_" + str(win)
        winstr = ('''\"{0}\" = WINDOW
    GLASS-TYPE = \"{1}\"
    X = {2}
    HEIGHT = {3}
    WIDTH = {4}
    OVERHANG-D = {5}
    LEFT-FIN-D = {6}
    RIGHT-FIN-D = {7}
    ..'''.format(wn_name, gl_type, x, wn_height, wn_width, hang_depth, l_fin_depth, r_fin_depth))
        x += wn_width + x_offset
        winlist.append(winstr)
        print (winstr)
  
    return winlist
    


def window_split(wl_name, 
                 num_win,
                 wn_width, 
                 wn_height, 
                 wn_offset,
                 l_fin_depth, 
                 r_fin_depth, 
                 hang_depth, 
                 gl_type,
                 x_start):
    '''takes some arguments (all mandatory for now,
    prints input-file-ready syntax and also returns a list of
    input-ready syntax for each window.'''
    
    x_offset = wn_width + wn_offset
    x_offset = wn_offset    

    x = x_start
    winlist = []
    for win in range(num_win):
        wn_name = wl_name + "_win_" + str(win)
        winstr = ('''\"{0}\" = WINDOW
    GLASS-TYPE = \"{1}\"
    X = {2}
    HEIGHT = {3}
    WIDTH = {4}
    OVERHANG-D = {5}
    LEFT-FIN-D = {6}
    RIGHT-FIN-D = {7}
    ..'''.format(wn_name, gl_type, x, wn_height, wn_width, hang_depth, l_fin_depth, r_fin_depth))
        x += wn_width + x_offset
        winlist.append(winstr)
        print (winstr)
  
    return winlist
    
'''
    
    example usage:
    
make_louvers(wl_name = "F2East Wall (G.E31.E44)",
             wl_width = 40,
             wn_width = 3,
             wn_height = 9,
             wn_offset = 0.5,
             l_fin_depth = 1,
             r_fin_depth = 2,
             hang_depth = 3,
             gl_type = "Glazing Type 1",
             x_start = 0
             )'''

             
             
             
             
#             
#make_louvers(wl_name = "Window 125",
#             wl_width = 70,
#             wn_width = 2,
#             wn_height = 10,
#             wn_offset = 0,
#             l_fin_depth = .5,
#             r_fin_depth = .5,
#             hang_depth = 0,
#             gl_type = "Prop Windows",
#             x_start = 42.5
#             )
#



'''
window_split(wl_name = "OPR",
             num_win = 4,
             wn_width = 3,
             wn_height = 5,
             wn_offset = 0,
             l_fin_depth = 0,
             r_fin_depth = 0,
             hang_depth = 0,
             gl_type = "Prop Windows",
             x_start = 2.5
             )'''


window_split(wl_name = "F1 win 5",
             num_win = 4,
             wn_width = 3.3,
             wn_height = 26,
             wn_offset = 0,
             l_fin_depth = 1.3,
             r_fin_depth = 1.3,
             hang_depth = 0,
             gl_type = "CW Win",
             x_start = 0
             )





