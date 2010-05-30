"""Web absorption computation
"""
import sys
import os
os.environ[ 'HOME' ] = '/tmp/'
import webabsorb

#This expects an input file with the following information
# 1: chemical formula 
# 2: radius of sample in mm
# 3: name for graphic file (/tmp/result.png)
# 4: flag for wavelength/energy (0 for energy, 1 for wavelength)
# 5: wavelength/energy value (selected by above)
# 6: flag for density/packing fraction (0 for density, 1 for packing fraction)
# 7: packing fraction/density value (selected by above)
''' Sample input:
C60Xe
0.35
/tmp/testout.png
1
0.35
0
5
'''

# note: a formula contains elements numbers and optional spaces only 
#        for example: 'C4 H9', 'H2O', 'MGO' or 'O MG' not 'OMG'


formula = sys.stdin.readline().strip()
Radius = float(sys.stdin.readline())
graphic = sys.stdin.readline().strip()
ifwave = sys.stdin.readline()
if ifwave:
    Wave = float(sys.stdin.readline())
    Energy = 0
else:
    Wave = 0
    Energy = float(sys.stdin.readline())
ifpack = sys.stdin.readline()
if ifpack:
    Packing = float(sys.stdin.readline())
    InputDensity = 0
else:
    Packing = 0
    InputDensity = float(sys.stdin.readline())

try:
#calc = webabsorb.Absorb(0.3, Wave=1, InputDensity=10, Packing=0.66)
    calc = webabsorb.Absorb(0.3,  Wave=Wave, Energy=Energy, Packing=0.66)

    calc.SetElems(formula)
    calc.ComputeMu()
    calc.SaveFig(graphic, format='png' )
except Exception, err:
    print "Error:", err
    
