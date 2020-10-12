import numpy as np
import pandas as pd

class DownInstance():
    def __init__(self,end_time,down):
        self.end_time = end_time
        self.down=down

    def __eq__(self, other):
        return (self.end_time == other.end_time)

    def __ne__(self, other):
        return self.end_time != other.end_time

    def __lt__(self, other):
        return (self.end_time < other.end_time)

    def __le__(self, other):
        return (self.end_time<=other.end_time)

    def __gt__(self, other):
        return (self.end_time>other.end_time)

    def __ge__(self, other):
        return (self.end_time >= other.end_time)

