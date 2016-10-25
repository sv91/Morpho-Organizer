import sys

from parser import *

dmg = False
index = False
morphologies = []

for arg in sys.argv:
    if (arg =="--index"):
        index = True
    if (arg =="--dmg"):
        dmg = True
    if ".geo" in arg:
        morphologies.append(arg)

results = parseMorphologies(morphologies, 0, 100)

f = open('results.geo', 'w')
f.write(results[0])
if dmg:
    g = open('results.cpp', 'w')
    g.write(results[1])

if index:
    i = open('results.txt', 'w')
    i.write(results[2])
