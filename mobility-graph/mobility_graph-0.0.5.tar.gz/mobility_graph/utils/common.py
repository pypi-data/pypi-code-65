"""
Ayman Mahmoud - August 2020

Resources:
https://rosettacode.org/wiki/Haversine_formula#Python
https://github.com/joshchea/gtfs-route-server/blob/master/scripts/GTFS_RouteServer.py

# 👍

"""
from math import radians, sin, cos, sqrt, asin, pi, atan2
import networkx as nx
import os

import sys
import inspect
import heapq, random
import csv, requests, json



DIS_LIM = 2000 # meters

class Stack:
    "A container with a last-in-first-out (LIFO) queuing policy."
    def __init__(self):
        self.list = []

    def push(self,item):
        "Push 'item' onto the stack"
        self.list.append(item)

    def pop(self):
        "Pop the most recently pushed item from the stack"
        return self.list.pop()

    def isEmpty(self):
        "Returns true if the stack is empty"
        return len(self.list) == 0

class Path(object):
    "A container with all possible paths between two points. [OD]"

    def __init__(self):
        self.list = []
        self.duration = 0
        self.mode = []
        self.walk_score = [] # Walk Score is an idea where the

    def push(self,item):
        "Push 'item' onto the stack"
        self.list.append(item)

    def pop(self):
        "Pop the most recently pushed item from the stack"
        return self.list.pop()

    def isEmpty(self):
        "Returns true if the stack is empty"
        return len(self.list) == 0

    def sort(self, key):
        """
        sort the path based on one of the metrics (duration, cost, n. of stops)
        :param key:
        :return:
        """
        pass

    def visualize(self, style):
        """
        uses node data and mode to visualize the path on a map
        : param "style": to choose how to display the path.
        :return: either an html link to the path or a graph or even download
        """

    def save_path(self):
        """
        saves the path object in a little description text file or xml file and a picture of the path
        :return:
        """

    def analyze(self, key):
        """
        returns a path based on the key given (must have a station 'x', cheapest, fastest)
        if left none we return all metrics in a table (such as GTFSTK style)
        :param key:
        :return:
        """
        pass

class Queue:
    "A container with a first-in-first-out (FIFO) queuing policy."
    def __init__(self):
        self.list = []

    def push(self,item):
        "Enqueue the 'item' into the queue"
        self.list.insert(0,item)

    def pop(self):
        """
          Dequeue the earliest enqueued item still in the queue. This
          operation removes the item from the queue.
        """
        return self.list.pop()

    def isEmpty(self):
        "Returns true if the queue is empty"
        return len(self.list) == 0

class PriorityQueue:
    """
      Implements a priority queue data structure. Each inserted item
      has a priority associated with it and the client is usually interested
      in quick retrieval of the lowest-priority item in the queue. This
      data structure allows O(1) access to the lowest-priority item.
    """
    def  __init__(self):
        self.heap = []
        self.count = 0

    def push(self, item, priority):
        entry = (priority, self.count, item)
        heapq.heappush(self.heap, entry)
        self.count += 1

    def pop(self):
        (_, _, item) = heapq.heappop(self.heap)
        return item

    def isEmpty(self):
        return len(self.heap) == 0

    def update(self, item, priority):
        # If item already in priority queue with higher priority, update its priority and rebuild the heap.
        # If item already in priority queue with equal or lower priority, do nothing.
        # If item not in priority queue, do the same thing as self.push.
        for index, (p, c, i) in enumerate(self.heap):
            if i == item:
                if p <= priority:
                    break
                del self.heap[index]
                self.heap.append((priority, c, item))
                heapq.heapify(self.heap)
                break
        else:
            self.push(item, priority)


def raiseNotDefined():
    fileName = inspect.stack()[1][1]
    line = inspect.stack()[1][2]
    method = inspect.stack()[1][3]

    print("*** Method not implemented: %s at line %s of %s" % (method, line, fileName))
    sys.exit(1)

def proceed():
    """
    Pauses the output stream awaiting user feedback.
    """
    input("<Press enter/return to continue>")

################################
# For map images
################################

import matplotlib.pyplot as plt
import numpy as np

import math
from urllib.request import urlopen
from io import StringIO
from PIL import Image


def deg2num(lat_deg, lon_deg, zoom):
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
    return (xtile, ytile)


def num2deg(xtile, ytile, zoom):
    n = 2.0 ** zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return (lat_deg, lon_deg)

"""
# Commented for now because it gives a warning
import matplotlib.pyplot as plt

import tilemapbase
#tilemapbase.start_logging()

def get_map(loc):
    
    #https: // github.com / MatthewDaws / TileMapBase / blob / master / notebooks / Example.ipynb
    

    tilemapbase.init(create=True)
    # Use open street map
    t = tilemapbase.tiles.build_OSM()
    degree_range = 0.003
    extent = tilemapbase.Extent.from_lonlat(loc[0] - degree_range, loc[0] + degree_range,
                                            loc[1] - degree_range, loc[1] + degree_range)
    extent = extent.to_aspect(1.0)

    fig, ax = plt.subplots(figsize=(8, 8), dpi=100)
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)

    plotter = tilemapbase.Plotter(extent, t, width=600)
    plotter.plot(ax, t)

    x, y = tilemapbase.project(*loc)
    ax.scatter(x, y, marker=".", color="black", linewidth=20)

    fig.show()

"""

def computeGCD(lat1,lon1,lat2,lon2):
    #computes great circle distance from lat/lon
    '''lat1/lon1 = lat/lon of first pt
       lat2/lon2 = lat/lon of second pt
    '''
    degRad = pi/180
    lat1 = degRad*lat1
    lon1 = degRad*lon1
    lat2 = degRad*lat2
    lon2 = degRad*lon2
    dellambda = lon2-lon1
    Numerator = sqrt((cos(lat2)*sin(dellambda))**2 + (cos(lat1)*sin(lat2)- sin(lat1)*cos(lat2)*cos(dellambda))**2)
    Denominator = sin(lat1)*sin(lat2) + cos(lat1)*cos(lat2)*cos(dellambda)
    delSigma = atan2(Numerator,Denominator)

    return 3963.19059*delSigma


def compute_HS(lat1, lon1, lat2, lon2):
    # computes haversine distance from lat/lon
    '''lat1/lon1 = lat/lon of first pt
       lat2/lon2 = lat/lon of second pt
    '''
    R = 6372.8  # Earth radius in kilometers

    dLat = radians(lat2 - lat1)
    dLon = radians(lon2 - lon1)
    lat1 = radians(lat1)
    lat2 = radians(lat2)

    a = sin(dLat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dLon / 2) ** 2
    c = 2 * asin(sqrt(a))

    return R * c

