#!/usr/bin/env python

from localwarming import *

df = WarmingDataFactory('data/TerreHauteRegional.dat')
model = WarmingModel(df.data())
constants = model.solve()
for i in range(len(constants)):
    print("X_{0} = {1}".format(i, constants[i]))
plot = WarmingPlot(df.data(), constants)
plot.show(['solution', 'trendline'])