'''
 #####
#     #  ####   ####  #   ##   #      #      #   #
#       #    # #    # #  #  #  #      #       # #
 #####  #    # #      # #    # #      #        #
      # #    # #      # ###### #      #        #
#     # #    # #    # # #    # #      #        #
 #####   ####   ####  # #    # ###### ######   #

######
#     # ###### ##### ###### #####  #    # # #    # ###### #####
#     # #        #   #      #    # ##  ## # ##   # #      #    #
#     # #####    #   #####  #    # # ## # # # #  # #####  #    #
#     # #        #   #      #####  #    # # #  # # #      #    #
#     # #        #   #      #   #  #    # # #   ## #      #    #
######  ######   #   ###### #    # #    # # #    # ###### #####
'''

"""
This module contains simple, general functions for a variety of uses.
"""

import matplotlib.pyplot as plt 

def set_sd_plots():
  """
  Set matplotlib parameters for standardized plots.

  Sets the size of the fonts for the legend, axes, and ticks.
  """
  params = {'legend.fontsize': 'xx-large',
          'legend.title_fontsize': 'xx-large',
          'figure.figsize': (27, 18),
          'axes.labelsize': 'xx-large',
          'axes.titlesize':'xx-large',
          'xtick.labelsize':'xx-large',
          'ytick.labelsize':'xx-large'}
          
  plt.rcParams.update(params)