from simnibs import sim_struct, run_simnibs
from math import sin, cos, radians
import os
from checkfired import checkFired
from rmtree import rmtree
import csv


if os.path.isfile('output.csv'):
    os.remove('output.csv')

if os.path.exists('simNibsOut\\'):
    rmtree('simNibsOut\\')



coilPos = [-41.2, 71.4, 55.3]

data = []

with open('output.csv', 'w', newline='') as csvfile:
    fieldnames = ['angle', 'fired', 'Mean_ROI', 'E1', 'E2', 'E3', 'MagnE']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for a in range(0, 345, 15):
        print("Calculating Positions for angle " + str(a))
        rad = radians(a)
        dx = sin(rad)
        dy = cos(rad)

        x = -41.2 + dx
        y = 71.4 + dy
        z = (-41.2 * (x + 41.2) + 71.4 * (y - 71.4)) / (-55.3) + 55.3

        coilDirRef = [x, y, z]
        print("Done!")

        print("\nRunning SimNIBS...")
        s = sim_struct.SESSION()

        s.subpath = 'm2m_ernie'

        s.pathfem = 'simNibsOut\\'

        tmslist = s.add_tmslist()

        tmslist.fnamecoil = 'Magstim_70mm_Fig8.ccd'

        pos = tmslist.add_position()

        pos.centre = coilPos
        pos.pos_ydir = coilDirRef

        run_simnibs(s)

        print("Done!")
        print("\nRunning Neuron scripts...")
        os.system('hocScript.bat')
        
        print("Done!")

        print("\nRunning BeNeMo...")
        fired = checkFired()
        #data.append((a, fired))
        mean_val= []
        with open('output.txt') as file:
            mean_val = [line.rstrip() for line in file]

        writer.writerow({'angle': a, 'fired': fired, 'Mean_ROI': mean_val[0], 'E1': mean_val[1], 'E2': mean_val[2], 'E3': mean_val[3], 'MagnE': mean_val[4]})
        #os.remove('output.txt')
        print("Done!")

        rmtree('simNibsOut')

    #write_to_csv('output.csv', data)
