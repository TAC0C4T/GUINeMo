import numpy as np
import io
import time
import sys
import subprocess
import datetime
import math
#This is the "outer file" for the whole automation process. This is the file you will execute.
#First, you will need to place the parameters.txt file in your Code\E-Field_Coupling\ folder.
#Second, check lines 30, 34, 40, and 63 of this file and change the folder locations to that of your own computer.
#in the automate_NeMo.bat file, change lines 9 and 12 to match that of your own computer
#
#If you are going to be doing more than one pulse, you will NEED to change line 21 of the automate_NeMo.bat file. the timeout needs to be scaled based off the number of pulses
#Make the timeout value equal to 100 times the number of pulses. It is 100 as default for one pulse
#The results will be saved to the location in line 63 of this file
#
#
def checkUniformFired(firedLow, firedHigh, firedTolerance) -> int:
    filevar = r"C:/"
    tolerance =firedTolerance#tolerance is a variable that can be changed here. GREATLY affects duration of code
    low =firedLow
    high =firedHigh#THIS MUST BE SET HIGHER THAN THE THRESHOLD. I DO NOT KNOW WHAT WILL HAPPEN OTHERWISE
    counter =0
    fired=0
    output = []#must declare the list as empty to start the program
    scale_inject = round(low + (high - low)/2)#sets starting value to the midpoint
    #below is the while loop to dial in the scaling factor
    while ((low + tolerance <=scale_inject) or (high -tolerance >=scale_inject)):#will quit the program once we are in range of the tolerance
        print('we are on run ' + str(counter))
        print('we are using scaling factor ' + str(scale_inject))
        #the next 6 lines deposit the scaling factor into params file to be used by NeMo
        with open(r'..\Results\NEURON\params.txt','r') as file:#this gets the values in the file and saves them to list
            filedata = file.readlines()
        stowrite = 'TMSAMP ' + str(scale_inject) + '\n'#this line and the next edit the list of the file
        filedata[2] = stowrite

        with open(r'..\Results\NEURON\params.txt','w') as file:#writes the new list to the same file
            file.writelines(filedata)

        #below is calling the batch file to compile everything
        subprocess.call(['automate_NeMo.bat'])


        myfile = np.loadtxt(r'..\Results\NEURON\voltage_trace.dat', skiprows = 0)#loading the voltage trace file to check if it fired
        #shape is in format row, col
        max_val = np.amax(myfile)

        if (max_val > 0):#it fired
            high =scale_inject
            print("It fired")
            fired =1#this is basically boolean that will be stored in the output file. no functional use
            scale_inject = round(low + (high-low)/2)#checks a midvalue in between high and low
        else:#it did not fire
            low = scale_inject
            print("It didn't fire")
            fired=0
            scale_inject = round(low + (high-low)/2)


        counter = counter+1
    return scale_inject


