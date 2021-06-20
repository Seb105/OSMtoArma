import numpy as np
from math import inf
import time
def cart2pol(coords):
    dist = np.sqrt(coords[0]**2 + coords[1]**2)
    angle = np.arctan2(coords[1], coords[0])
    return dist, angle

def pol2cart(angle, dist):
    x = dist * np.cos(angle)
    y = dist * np.sin(angle)
    return np.asarray([x, y])

def get_dist(p1, p2):
    d = p2-p1
    return np.hypot(d[0], d[1])

def get_angle(p1, p2, return_radians=False):
    d = p2-p1
    angle = np.arctan2(d[0], d[1])
    if return_radians:
        return angle
    else:
        return np.degrees(angle)

def nearest_value(target, values):
    diff = inf
    for value in values:
        this_diff = abs(value - target)
        if this_diff < diff: 
            result = value
            diff = this_diff
    return result

class Progress_bar():
    def __init__(self, activity, count):#
        self.activity = activity
        self.count = count
        self.i = -1
        self.barlength = 20
        self.last_update = time.time()
        self.start_time = self.last_update
        print("")
        self.update_progress()

    def print_in_progress(self, string):
        print(string)
        print("")

    def update_exact(self, i):
        self.i = i-1
        self.update_progress()

    def update_progress(self):
        self.i += 1
        progress = self.i/self.count
        if self.last_update+1<time.time() or progress >= 1:
            self.last_update=time.time()
            block = int(round(self.barlength*progress))
            seconds_remaining = int(((time.time() - self.start_time)/progress) * (1-progress))
            text = "{0}: [{1}] {2}%. {3} seconds remaining".format(self.activity, "#"*block + "-"*(self.barlength-block), round(progress*100, 2), seconds_remaining)
            lineEnd = '\r' if progress<1.0 else '\n\n'
            print("                                                                                               ", end="\r")
            print(text, end=lineEnd)
