from coopr.pyomo import *
from coopr.opt import *
import math
import time

class WarmingModel:
    data = ([], [])
    
    def __init__(self, data):
        self._timestamp = None
        self._tsAccum = 0.0
        self.timestamp()
        self.data = data
        self.solution = None
    
    # Helpers
    def timestamp(self):
        """Mark the current time of execution. If not the first call to
        timestamp(), return the difference in time since the last call.
        Accumulate time since last call."""
        curTime = time.time()
        lastTime = self._timestamp
        self._timestamp = curTime
        if lastTime != None:
            tdiff = curTime - lastTime
            self._tsAccum += tdiff
            return tdiff
    def ts_accumulated(self):
        return self._tsAccum
    
    @staticmethod
    def modelFunction(x, d):
        return x[0] + x[1] * d + x[2] * math.cos(2 * math.pi * d / 365.25) + x[3] * math.sin(2 * math.pi * d / 365.25) \
                    + x[4] * math.cos(2 * math.pi * d / (10.7 * 365.25)) + x[5] * math.sin(2 * math.pi * d / (10.7 * 365.25))
    
    def solve(self):
        print("Beginning solve with {0} dates and {1} temps".format(len(self.data[0]), len(self.data[1])))
        
        # model
        M = Model()
        
        # sets
        M.Dates = Set(initialize=self.data[0])
        M.XRange = RangeSet(0,5)
        
        # parameters
        def InitAvg(d, M):
            #if d not in self.data[0]:
            #    print("Can't find {0} in data list; quitting...".format(d))
            #    quit()
            return self.data[1][self.data[0].index(d)]
        M.Avg = Param(M.Dates, initialize=InitAvg)
        
        def InitDay(d, M):
            return self.data[0].index(d) + 1
        M.Day = Param(M.Dates, initialize=InitDay)
        
        # variables
        M.X = Var(M.XRange, domain=Reals)
        M.Dev = Var(M.Dates, domain=NonNegativeReals)
        
        # objective
        def CalcSumDev(M):
            return sum(M.Dev[d] for d in M.Dates)
        M.SumDev = Objective(rule=CalcSumDev, sense=minimize)
        
        # constraints
        def CalcDefPosDev(d, M):
            return self.modelFunction(M.X, M.Day[int(d)]) - M.Avg[d] <= M.Dev[d]
        M.RequireDefPosDev = Constraint(M.Dates, rule=CalcDefPosDev)
        
        def CalcDefNegDev(d, M):
            return -1 * M.Dev[d] <= self.modelFunction(M.X, M.Day[int(d)]) - M.Avg[d]
        M.RequireDefNegDev = Constraint(M.Dates, rule=CalcDefNegDev)
        
        # solve
        print("Set up Model object: {0}s".format(self.timestamp()))
        instance = M.create()
        print("Created instance: {0}s".format(self.timestamp()))
        opt = SolverFactory("gurobi")
        opt.keepFiles = False
        soln = opt.solve(instance)
        print("Solved instance: {0}s".format(self.timestamp()))
        print("Total time: {0}s".format(self.ts_accumulated()))
        
        x = []
        for i in range(6):
            x.append(soln.Solution.Variable.X[i].Value)
        self.solution = x
        return x
    
    def deviations(self):
        if self.solution == None:
            self.solve()
        
        def actual(d):
            return self.data[1][self.data[0].index(d)]
        
        def day(d):
            return self.data[0].index(d) + 1
        
        def expected(d):
            return self.modelFunction(self.solution, day(d))
        
        return [actual(d) - expected(d) for d in self.data[0]]