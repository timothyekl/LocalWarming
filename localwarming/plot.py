#!/usr/bin/python
# Requires Apple python for Gurobi compatibility :P

import math
import pylab
import re
import sys

PI = 4 * math.atan(1)

class WarmingPlot:
    dates = []
    temps = []
    
    def __init__(self, data, constants):
        self.data = data
        self.constants = constants
    
    # Model function
    def solnVal(self, x):
        return self.constants[0] + self.constants[1] * x + self.constants[2] * math.cos(2 * PI * x / 365.25) \
                                + self.constants[3] * math.sin(2 * PI * x / 365.25) \
                                + self.constants[4] * math.cos(2 * PI * x / (365.25 * 10.7)) \
                                + self.constants[5] * math.sin(2 * PI * x / (365.25 * 10.7))
    
    def trendVal(self, x):
        return self.constants[0] + self.constants[1] * x
    
    def show(self, plotparts):
        # TODO refactor so it uses actual data structure instead of rereading file
        with open('data/TerreHauteRegional.dat', 'r') as f:
            i = 0
            for line in f:
                match = re.search('\s+(\d{8})\s+(-?\d{1,2}\.\d{1})\s', line)
                if not match:
                    print("Failed to find match for line: {0}".format(line))
                else:
                    self.dates.append(int(match.group(1)))
                    self.temps.append(float(match.group(2)))
                    i = i + 1
        
        if len(self.dates) == len(self.temps):
            print("Confirmed lengths match ({0} items); plotting...".format(len(self.dates)))
            pylab.scatter(list(range(len(self.temps))),self.temps)
            
            for arg in plotparts:
                if arg == "solution":
                    pylab.plot([self.solnVal(x) for x in list(range(len(self.temps)))], 'r', linewidth=3)
                elif arg == "trendline":
                    pylab.plot([self.trendVal(x) for x in list(range(len(self.temps)))], 'g',linewidth=3)
            
            pylab.show()