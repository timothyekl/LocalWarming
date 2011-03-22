#!/usr/bin/env python

from localwarming import *
import pprint

#startdate, enddate = 20000101, 20091231 # fixed: ten years
#startdate, enddate = 19900102, 20091231 # fixed: twenty years
#startdate, enddate = None, 19900206 # before sensor move
#startdate, enddate = 19900208, None # after sensor move
startdate, enddate = None, None # all data

df = WarmingDataFactory('data/TerreHauteRegional.dat')

solver = WarmingSolver(df.getDates(startdate=startdate, enddate=enddate), df.getTemps(startdate=startdate, enddate=enddate))

#solver.DISABLE_VARIABILITY_CHECK = True
#solver.DISABLE_CYCLE_LENGTH_CHECK = True
#solver.DISABLE_CONFIDENCE_INTERVALS = True

soln = solver.solve()

for i in range(len(soln['fit'])):
    print("X_{0} = {1} +- {2}".format(i, soln['fit'][i][0], soln['fit'][i][1]))

plot = WarmingDataPlot(df.getDates(startdate=startdate, enddate=enddate), df.getTemps(startdate=startdate, enddate=enddate), [c[0] for c in soln['fit']])
plot.draw(['solution', 'trendline'])

deviations = solver.fitDeviations()
devPlot = WarmingDeviationPlot(deviations)
devPlot.draw()

minDevPlot = WarmingMinDeviationPlot(soln['cycle'][0], soln['cycle'][1])
minDevPlot.draw()

raw_input("Press Enter to exit")