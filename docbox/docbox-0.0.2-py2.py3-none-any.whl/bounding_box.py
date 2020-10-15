class BoundingBox(object):
    def __init__(self, x1=None, x2=None, y1=None, y2=None, w=None, h=None):
        self.x1 = x1
        self.x = x1
        self.x2 = x2 or x1 + w
        self.y1 = y1
        self.y2 = y2 or y1 + h
        self.y = y1
