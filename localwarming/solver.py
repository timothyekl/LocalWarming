from model import WarmingModel
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
        self.fitModel = WarmingModel(self.data)
        constants = self.fitModel.solve()
        devs = self.deviations()
        
        random.seed()
        randDays = [random.choice(self.data[1]) for i in list(range(len(self.data[1])))]
        
        
        return [(x,0) for x in constants]
    
    def deviations(self):
        return self.fitModel.deviations()