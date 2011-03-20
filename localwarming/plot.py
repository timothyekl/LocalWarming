import math
import pylab
import re
import sys

PI = 4 * math.atan(1)

class WarmingPlot:
    def __init__(self, data, constants):
        """Prepares a plot object with constants from a model and data
        from a data factory. The `data` struct needs to be a 2-tuple of
        lists containing dates and temperatures, in that order."""
        # Save full data object, just in case
        self.data = data
        self.dates = data[0]
        self.temps = data[1]
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
        if len(self.dates) == len(self.temps):
            pylab.scatter(list(range(len(self.temps))),self.temps)
            
            for arg in plotparts:
                if arg == "solution":
                    pylab.plot([self.solnVal(x) for x in list(range(len(self.temps)))], 'r', linewidth=3)
                elif arg == "trendline":
                    pylab.plot([self.trendVal(x) for x in list(range(len(self.temps)))], 'g',linewidth=3)
            
            pylab.show()
        else:
            print("Given inappropriate data (dates and temps don't match); quitting")
            quit()