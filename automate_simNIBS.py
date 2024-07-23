from simnibs import sim_struct, run_simnibs
from math import sin, cos, radians
import os
from checkfired import checkFired
from rmtree import rmtree
import csv
import shutil
import glob
import sys
import subprocess

# Initializing variables
# Angles in degrees
coilPos = [-41.2, 71.4, 55.3] # Coil position [x, y, z]
initialAngle = 0 # First angle to test
finalAngle = 360 # End angle (does not check this angle)
step = 15 # Step value in degrees between each tested angle

data = []

# Sanity checks. Code may work without this
if os.path.isfile('output.csv'):
    os.remove('output.csv')

if os.path.exists('simNibsOut\\'):
    rmtree('simNibsOut\\')

if not os.path.exists('simNibsPastOutputs'):
    os.mkdir('simNibsPastOutputs')

# Setting up CSV file
with open('output.csv', 'w', newline='') as csvfile:
    fieldnames = ['angle', 'fired', 'Mean_ROI', 'E1', 'E2', 'E3', 'MagnE']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    # Main loop
    for a in range(initialAngle, finalAngle, step):

        outFolder = 'simNibsPastOutput' + str(a)
        trueOut = 'simNibsPastOutputs\\' + outFolder

        # Seeing if output has been created in previous run to save a sweet sweet 60 seconds or so every iteration
        # i promise it adds up
        # os.path.exists(trueOut)
        if os.path.exists(trueOut):
            print("Found pre-existing mesh at " + trueOut)
            meshPath = trueOut + '\\'
        else:

            # Calculating direction reference coordinates
            print("Calculating Positions for angle " + str(a))
            ref = [0, 13.58, -21]
            normal = [coilPos[i] - ref[i] for i in range(3)]
            rad = radians(a)
            dx = sin(rad)
            dy = cos(rad)
            xd = coilPos[0] + dx
            yd = coilPos[1] + dy
            zd = coilPos[2] + (-normal[0] * (xd - coilPos[0]) - normal[1] * (yd - coilPos[1])) / normal[2] # Equation provided in simulation parameters doc, solved for z

            coilDirRef = [xd, yd, zd]
            print("Done!")


            # SimNIBS code
            print("\nRunning SimNIBS...")
            s = sim_struct.SESSION()

            s.subpath = 'm2m_ernie'

            s.pathfem = 'simNibsOut\\'

            tmslist = s.add_tmslist()

            tmslist.fnamecoil = 'Magstim_70mm_Fig8.ccd'

            pos = tmslist.add_position()

            pos.centre = coilPos
            pos.pos_ydir = coilDirRef
            pos.distance = 2

            run_simnibs(s)

            print("Done!")
            meshPath = 'simNibsOut\\'

        # Running file to run neuron and matlab scripts
        print("\nRunning Neuron scripts...")
        #os.system('hocScript.ps1 ' + meshPath)
        p = subprocess.Popen(["powershell.exe", os.getcwd() + "\\hocScript.ps1", meshPath], stdout=sys.stdout)
        p.communicate()
        print("Done!")

        print("\nRunning BeNeMo...")
        fired = checkFired()


        #making csv
        mean_val= []
        with open('output.txt') as file:
            mean_val = [line.rstrip() for line in file]

        writer.writerow({'angle': a, 'fired': fired, 'Mean_ROI': mean_val[0], 'E1': mean_val[1], 'E2': mean_val[2], 'E3': mean_val[3], 'MagnE': mean_val[4]})
        print("Done!")


        # Cleanup
        if os.path.exists('simNibsOut\\'):
            os.rename('simNibsOut', outFolder)
            shutil.move(outFolder, 'simNibsPastOutputs')
        for f in glob.glob("results*.txt"): # Globbin time
            os.remove(f)
