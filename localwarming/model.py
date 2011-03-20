from coopr.pyomo import *
from coopr.opt import *
import math
import time

class WarmingModel:
    # Configs
    USE_SOLAR_SHIFT = True
    
    data = ([], [])
    
    def __init__(self, data):
        self._timestamp = None
        self._tsAccum = 0.0
        self.timestamp()
        self.data = data
    
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
    
    def solve(self):
        # model
        M = Model()
        
        # sets
        M.Dates = Set(initialize=self.data[0])
        if self.USE_SOLAR_SHIFT:
            M.XRange = RangeSet(0,5)
        else:
            M.XRange = RangeSet(0,3)
        
        # parameters
        def InitAvg(d, M):
            if d not in self.data[0]:
                print("Can't find {0} in data list; quitting...".format(d))
                quit()
            return self.data[1][self.data[0].index(d)]
        M.Avg = Param(M.Dates, initialize=InitAvg)
        
        def InitDay(d, M):
            return self.data[0].index(d) + 1
        M.Day = Param(M.Dates, initialize=InitDay)
        
        PI = 4 * atan(1)
        
        # variables
        M.X = Var(M.XRange, domain=Reals)
        M.Dev = Var(M.Dates, domain=NonNegativeReals)
        
        # objective
        def CalcSumDev(M):
            return sum(M.Dev[d] for d in M.Dates)
        M.SumDev = Objective(rule=CalcSumDev, sense=minimize)
        
        # constraints
        def CalcDefPosDev(d, M):
            if self.USE_SOLAR_SHIFT:
                return M.X[0] + M.X[1] * M.Day[int(d)] \
                            + M.X[2] * math.cos(2 * PI * M.Day[int(d)] / 365.25) \
                            + M.X[3] * math.sin(2 * PI * M.Day[int(d)] / 365.25) \
                            + M.X[4] * math.cos(2 * PI * M.Day[int(d)] / (10.7 * 365.25)) \
                            + M.X[5] * math.sin(2 * PI * M.Day[int(d)] / (10.7 * 365.25)) \
                            - M.Avg[d] \
                        <= M.Dev[d];
            else:
                return M.X[0] + M.X[1] * M.Day[d] \
                            + M.X[2] * math.cos(2 * PI * M.Day[int(d)] / 365.25) \
                            + M.X[3] * math.sin(2 * PI * M.Day[int(d)] / 365.25) \
                            - M.Avg[d] \
                        <= M.Dev[d];
        M.RequireDefPosDev = Constraint(M.Dates, rule=CalcDefPosDev)
        
        def CalcDefNegDev(d, M):
            if self.USE_SOLAR_SHIFT:
                return -1 * M.Dev[d] <= \
                    M.X[0] + M.X[1] * M.Day[int(d)] \
                            + M.X[2] * math.cos(2 * PI * M.Day[int(d)] / 365.25) \
                            + M.X[3] * math.sin(2 * PI * M.Day[int(d)] / 365.25) \
                            + M.X[4] * math.cos(2 * PI * M.Day[int(d)] / (10.7 * 365.25)) \
                            + M.X[5] * math.sin(2 * PI * M.Day[int(d)] / (10.7 * 365.25)) \
                            - M.Avg[d];
            else:
                return -1 * M.Dev[d] <= \
                    M.X[0] + M.X[1] * M.Day[d] \
                            + M.X[2] * math.cos(2 * PI * M.Day[int(d)] / 365.25) \
                            + M.X[3] * math.sin(2 * PI * M.Day[int(d)] / 365.25) \
                            - M.Avg[d];
        M.RequireDefNegDev = Constraint(M.Dates, rule=CalcDefNegDev)
        
        # solve
        print("Set up Model object: {0}s".format(self.timestamp()))
        #instance = M.create("model-pyomo.dat")
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
        return x