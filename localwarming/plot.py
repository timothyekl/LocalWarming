import math
import pylab
import re
import sys

from localwarming import WarmingModel

class WarmingDataPlot:
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
        return WarmingModel.modelFunction(self.constants, x)
    
    def trendVal(self, x):
        return self.constants[0] + self.constants[1] * x
    
    def draw(self, plotparts):
        if len(self.dates) == len(self.temps):
            pylab.figure()
            pylab.scatter(list(range(len(self.temps))),self.temps)
            
            for arg in plotparts:
                if arg == "solution":
                    pylab.plot([self.solnVal(x) for x in list(range(len(self.temps)))], 'r', linewidth=3)
                elif arg == "trendline":
                    pylab.plot([self.trendVal(x) for x in list(range(len(self.temps)))], 'g',linewidth=3)
            
            pylab.draw()
        else:
            print("Given inappropriate data (dates and temps don't match); quitting")
            quit()

class WarmingDeviationPlot:
    def __init__(self, data):
        """Prepares a plot objects with deviations from a model. The
        `data` argument needs to be a simple list of deviation floats."""
        self.data = data
    
    def draw(self):
        pylab.figure()
        
        spread = math.ceil(max(self.data)) - math.floor(min(self.data))
        pylab.hist(self.data, bins=spread, normed=True)
        
        def normalValue(x):
            return 1 / math.sqrt(2 * math.pi * spread) * math.exp(-1 * x * x / (2 * spread))
        xlist = list(range(int(math.floor(min(self.data))), int(math.ceil(max(self.data))) + 1, 1))
        pylab.plot(xlist, [normalValue(x) for x in xlist], 'r', linewidth=2)
        
        pylab.draw()