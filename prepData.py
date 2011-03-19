#!/usr/bin/env python

import math
import os

PI = 4 * math.atan(1)

outPath = "model-pyomo-python.dat"
if os.path.exists(outPath):
    os.remove(outPath)

with open(outPath, 'w') as outFile:
    outFile.write("set Dates :=\n")
    with open("data/Dates.dat", 'r') as inFile:
        outFile.write(inFile.read())
    outFile.write(";\n")
    
    outFile.write("param Avg :=\n")
    with open("data/TerreHauteRegional.dat", 'r') as inFile:
        outFile.write(inFile.read())
    outFile.write(";\n")
    
    outFile.write("param Day :=\n")
    lineNo = 1
    with open("data/Dates.dat", 'r') as inFile:
        for line in inFile:
            outFile.write("{0} {1}.0\n".format(line.replace("\n", ""), lineNo))
            lineNo += 1
    outFile.write(";\n")
    
    outFile.write("param YearlySin :=\n")
    lineNo = 1
    with open("data/Dates.dat", 'r') as inFile:
        for line in inFile:
            outFile.write("{0} {1}\n".format(line.replace("\n", ""), math.sin(2 * PI * lineNo / 365.25)))
            lineNo += 1
    outFile.write(";\n")
    
    outFile.write("param YearlyCos :=\n")
    lineNo = 1
    with open("data/Dates.dat", 'r') as inFile:
        for line in inFile:
            outFile.write("{0} {1}\n".format(line.replace("\n", ""), math.cos(2 * PI * lineNo / 365.25)))
            lineNo += 1
    outFile.write(";\n")