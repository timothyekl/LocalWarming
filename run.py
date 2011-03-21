#!/usr/bin/env python

from localwarming import *
import pprint

df = WarmingDataFactory('data/TerreHauteRegional.dat')
solver = WarmingSolver(df.data())
soln = solver.solve()
for i in range(len(soln)):
    print("X_{0} = {1} +- {2}".format(i, soln[i][0], soln[i][1]))
plot = WarmingDataPlot(df.data(), [c[0] for c in soln])
plot.draw(['solution', 'trendline'])
deviations = solver.deviations()
devPlot = WarmingDeviationPlot(deviations)
devPlot.draw()
raw_input("Press Enter to exit")