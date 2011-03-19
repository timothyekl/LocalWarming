#!/usr/bin/python
# Needs Apple Python for Gurobi :P

from localwarming import *

model = WarmingModel()
constants = model.solve()
for i in range(len(constants)):
    print("X_{0} = {1}".format(i, constants[i]))
plot = WarmingPlot(None, constants)
plot.show(['solution', 'trendline'])