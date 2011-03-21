from model import WarmingModel
import math
import random

class WarmingSolver:
    """Wraps a number of WarmingModel objects to find both the model fit
    and confidence intervals for the fit."""
    
    def __init__(self, data):
        self.data = data
    
    def solve(self):
        """Pass off control to a number of WarmingModel objects and find
        a best fit with confidence intervals. Returns a list of fit
        constants as a list of tuples `(const, diff)`, where the interval
        is defined by `const +/- diff`."""
        
        # Do the actual run to find the fit and trendline
        self.fitModel = WarmingModel(self.data)
        constants = self.fitModel.solve()
        devs = self.deviations()
        
        # Do a bunch more iterations to find a confidence interval for the above
        ITER_COUNT = 2
        random.seed()
        xstar = []
        for fuzzIter in range(ITER_COUNT):
            fuzzedTemps = [self.data[1][i] + random.choice(devs) for i in list(range(len(self.data[0])))]
            fuzzedModel = WarmingModel((self.data[0], fuzzedTemps))
            fuzzedConstants = fuzzedModel.solve()
            print("Fuzzy constants: " + str(fuzzedConstants))
            xstar.append(fuzzedConstants)
        
        # Actually compute the confidence interval
        stdevs = []
        for pos in range(len(constants)):
            cDevs = [(xstar[i][pos] - constants[pos]) ** 2 for i in range(ITER_COUNT)]
            cStdDev = math.sqrt(sum(cDevs) / float(len(cDevs)))
            stdevs.append(cStdDev)
        
        return [(constants[i], stdevs[i]) for i in range(len(constants))]
    
    def deviations(self):
        return self.fitModel.deviations()