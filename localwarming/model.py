from coopr.pyomo import *
from coopr.opt import *
import math
import pprint
import time

class WarmingModel:
    # Helpers
    def ts_init(self):
        self._timestamp = None
        self._tsAccum = 0.0
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
    
    @classmethod
    def modelFunction(cls, x, d, sc=10.7):
        return x[0] + x[1] * d + x[2] * math.cos(2 * math.pi * d / 365.25) + x[3] * math.sin(2 * math.pi * d / 365.25) \
                    + x[4] * math.cos(2 * math.pi * d / (sc * 365.25)) + x[5] * math.sin(2 * math.pi * d / (sc * 365.25))

class WarmingFitModel(WarmingModel):
    dates = []
    temps = []
    
    solarCycle = 10.7
    
    def __init__(self, dates, temps, solarCycle=10.7):
        self.ts_init()
        self.timestamp()
        self.dates = dates
        self.temps = temps
        self.solarCycle = solarCycle
        self.solution = None
    
    def solve(self):
        print("Beginning solve with {0} dates and {1} temps".format(len(self.dates), len(self.temps)))
        
        # model
        M = Model()
        
        # sets
        M.Dates = Set(initialize=self.dates)
        M.XRange = RangeSet(0,5)
        
        # parameters
        def InitAvg(d, M):
            #if d not in self.dates:
            #    print("Can't find {0} in data list; quitting...".format(d))
            #    quit()
            return self.temps[self.dates.index(d)]
        M.Avg = Param(M.Dates, initialize=InitAvg)
        
        def InitDay(d, M):
            return self.dates.index(d) + 1
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
            return self.modelFunction(M.X, M.Day[int(d)], self.solarCycle) - M.Avg[d] <= M.Dev[d]
        M.RequireDefPosDev = Constraint(M.Dates, rule=CalcDefPosDev)
        
        def CalcDefNegDev(d, M):
            return -1 * M.Dev[d] <= self.modelFunction(M.X, M.Day[int(d)], self.solarCycle) - M.Avg[d]
        M.RequireDefNegDev = Constraint(M.Dates, rule=CalcDefNegDev)
        
        # solve
        print("Set up fit model object: {0}s".format(self.timestamp()))
        instance = M.create()
        print("Created instance: {0}s".format(self.timestamp()))
        opt = SolverFactory("gurobi")
        opt.keepFiles = False
        soln = opt.solve(instance)
        print("Solved instance: {0}s".format(self.timestamp()))
        print("Total time: {0}s".format(self.ts_accumulated()))
        
        x = []
        for i in range(6):
            x.append(float(soln.Solution.Variable.X[i].Value))
        self.solution = x[:]
        
        return self.solution
    
    def deviations(self):
        if self.solution == None:
            self.solve()
        
        def actual(d):
            return self.temps[self.dates.index(d)]
        
        def day(d):
            return self.dates.index(d) + 1
        
        def expected(d):
            return self.modelFunction(self.solution, day(d), self.solarCycle)
        
        return [actual(d) - expected(d) for d in self.dates]

class WarmingVariabilityModel(WarmingModel):
    dates = []
    temps = []
    
    solarCycle = 10.7
    
    def __init__(self, dates, temps, xsub, operation, fitConstants, deltaStar, epsilon=0.0, solarCycle=10.7):
        self.ts_init()
        self.timestamp()
        self.dates = dates
        self.temps = temps
        self.xsub = xsub
        self.operation = operation
        self.fitConstants = fitConstants
        self.deltaStar = deltaStar
        self.epsilon = epsilon
        self.solarCycle = solarCycle
        self.solution = None
    
    def solve(self):
        print("Beginning solve with {0} dates and {1} temps".format(len(self.dates), len(self.temps)))
        
        # model
        M = Model()
        
        # sets
        M.Dates = Set(initialize=self.dates)
        
        # parameters
        def InitAvg(d, M):
            return self.temps[self.dates.index(d)]
        M.Avg = Param(M.Dates, initialize=InitAvg)
        
        def InitDay(d, M):
            return self.dates.index(d) + 1
        M.Day = Param(M.Dates, initialize=InitDay)
        
        # variables
        M.X = Var(domain=Reals)
        M.Dev = Var(M.Dates, domain=NonNegativeReals)
        
        # objective
        def CalcX(M):
            return M.X
        if self.operation == "min":
            M.XObj = Objective(rule=CalcX, sense=minimize)
        elif self.operation == "max":
            M.XObj = Objective(rule=CalcX, sense=maximize)
        else:
            raise "Problem: unknown operation passed to variability model"
        
        # constraints
        def CalcDefPosDev(d, M):
            xlist = [self.fitConstants[i] for i in range(len(self.fitConstants)) if i != self.xsub]
            xlist.insert(self.xsub, M.X)
            return self.modelFunction(xlist, M.Day[int(d)], self.solarCycle) - M.Avg[d] <= M.Dev[d]
        M.RequireDefPosDev = Constraint(M.Dates, rule=CalcDefPosDev)
        
        def CalcDefNegDev(d, M):
            xlist = [self.fitConstants[i] for i in range(len(self.fitConstants)) if i != self.xsub]
            xlist.insert(self.xsub, M.X)
            return -1 * M.Dev[d] <= self.modelFunction(xlist, M.Day[int(d)], self.solarCycle) - M.Avg[d]
        M.RequireDefNegDev = Constraint(M.Dates, rule=CalcDefNegDev)
        
        def CalcDeltas(M):
            return sum(M.Dev[d] for d in M.Dates) <= self.deltaStar + self.epsilon
        M.RequireDeltas = Constraint(rule=CalcDeltas)
        
        # solve
        print("Set up variability model object: {0}s".format(self.timestamp()))
        instance = M.create()
        print("Created instance: {0}s".format(self.timestamp()))
        opt = SolverFactory("gurobi")
        opt.keepFiles = False
        soln = opt.solve(instance)
        print("Solved instance: {0}s".format(self.timestamp()))
        print("Total time: {0}s".format(self.ts_accumulated()))
        
        self.solution = float(soln.Solution.Variable.X.Value)
        return self.solution
    
    def deviations(self):
        if self.solution == None:
            self.solve()
        
        def actual(d):
            return self.temps[self.dates.index(d)]
        
        def day(d):
            return self.dates.index(d) + 1
        
        def expected(d):
            return self.modelFunction(self.solution, day(d), self.solarCycle)
        
        return [actual(d) - expected(d) for d in self.dates]