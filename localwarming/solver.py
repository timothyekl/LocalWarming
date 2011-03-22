from model import WarmingFitModel, WarmingVariabilityModel
import gc
import math
import pprint
import random

class WarmingSolver:
    """Wraps a number of WarmingModel objects to find both the model fit
    and confidence intervals for the fit."""
    
    def __init__(self, dates, temps):
        self.dates = dates
        self.temps = temps
        self.data = (dates, temps)
    
    def solve(self):
        """Pass off control to a number of WarmingModel objects and find
        a best fit with confidence intervals. Returns a list of fit
        constants as a list of tuples `(const, diff)`, where the interval
        is defined by `const +/- diff`."""
        
        # Do the actual run to find the fit and trendline
        self.fitModel = WarmingFitModel(self.dates, self.temps)
        self.constants = self.fitModel.solve()
        self.devs = self.fitModel.deviations()
        
        # Verify the optimality of solutions
        xvariabilities = { "min" : [], "max" : [] }
        for op in xvariabilities.keys():
            for xsub in [0, 1]:
                variabilityModel = WarmingVariabilityModel(self.dates, self.temps, xsub, op, self.constants, sum(list(map(abs, self.devs))))
                xvariabilities[op].append(variabilityModel.solve())
        pprint.pprint(xvariabilities)
        
        # Do a bunch more iterations to find a confidence interval for the above
        ITER_COUNT = 0
        #ITER_COUNT = 50
        random.seed()
        xstar = []
        for fuzzIter in range(ITER_COUNT):
            fuzzedTemps = [self.temps[i] + random.choice(self.devs) for i in list(range(len(self.dates)))]
            fuzzedModel = WarmingFitModel(self.dates, fuzzedTemps)
            fuzzedConstants = fuzzedModel.solve()
            print("Fuzzy constants: " + str(fuzzedConstants))
            xstar.append(fuzzedConstants)
        
        # Actually compute the confidence interval
        stdevs = [0 for x in self.constants]
        if ITER_COUNT > 0:
            for pos in range(len(self.constants)):
                cDevs = [(xstar[i][pos] - self.constants[pos]) ** 2 for i in range(ITER_COUNT)]
                cStdDev = math.sqrt(sum(cDevs) / float(len(cDevs)))
                stdevs[pos] = cStdDev
        
        return [(self.constants[i], 2 * stdevs[i]) for i in range(len(self.constants))]
    
    def deviations(self):
        return self.devs