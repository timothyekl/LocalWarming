#!/usr/bin/env python

from localwarming import *
import pprint

df = WarmingDataFactory('data/TerreHauteRegional.dat')
solver = WarmingSolver(df.getDates(), df.getTemps())
solver.DISABLE_VARIABILITY_CHECK = True
solver.DISABLE_CYCLE_LENGTH_CHECK = True
solver.DISABLE_CONFIDENCE_INTERVALS = True
soln = solver.solve()
for i in range(len(soln['fit'])):
    print("X_{0} = {1} +- {2}".format(i, soln['fit'][i][0], soln['fit'][i][1]))
plot = WarmingDataPlot(df.getDates(), df.getTemps(), [c[0] for c in soln['fit']])
plot.draw(['solution', 'trendline'])
deviations = solver.fitDeviations()
devPlot = WarmingDeviationPlot(deviations)
devPlot.draw()
mindevPlot = WarmingMinDeviationPlot(soln['cycle'][0], soln['cycle'][1])
mindevPlot.draw()
raw_input("Press Enter to exit")