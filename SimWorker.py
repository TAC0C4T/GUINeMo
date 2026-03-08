from PyQt5.QtCore import QObject, QThread, pyqtSignal
import os
from rmtree import rmtree
import shutil
import csv
import subprocess
from checkfired import checkFired
from checkfiredUniform import checkUniformFired
import glob
from structs import paramSet, paramSetUniform
from math import cos, sin, radians
import sys

class SimWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(str)        # for sending log messages to the UI
    result_ready = pyqtSignal(dict)   # for sending each row's output back to UI


    def __init__(self, data, sim_type, find_threshold): 
        super().__init__()
        self.data = data
        self.sim_type = sim_type
        self.findThreshold = find_threshold

    
    def run(self):
        for params in self.data:
            if self.sim_type == 1:
                output = self.autoNIBSLoop(params)
                self.result_ready.emit({
                    'Pulse Shape': params.pulseType,
                    'Pulse Width (µs)': params.pulseWidth * 1000,
                    'Frequency (kHz)': 1 / params.ipi,
                    'Pulse Spacing (µs)': params.ipi * 1000,
                    '# of Pulses': params.numPulse,
                    'Coil Orientation (°)': params.angle,
                    'Pulse Length (µs)': params.pulseLength * 1000,
                    'Step Size (µs)': params.timeStep * 1000,
                    'Threshold Low': params.firedLow,
                    'Threshold High': params.firedHigh,
                    'Threshold Tolerance': params.firedTolerance,
                    'Coil Position x,y,z': ','.join(map(str, params.coilPos)),
                    'Neuron Position x,y,z': ','.join(map(str, params.neuronPos)),
                    'Neuron Orientation x,y,z': ','.join(map(str, params.neuronOrientation)),
                    'Neuron Axis x,y,z': ','.join(map(str, params.neuronAxis)),
                    'MagnE Normalized': output[6],
                    'Firing Threshold': output[1],
                    'MagnE (V/m)': output[6] * output[1],
                    'E1': output[3],
                    'E2': output[4],
                    'E3': output[5],
                    'Mean_ROI': output[2],
                })
            elif self.sim_type == 2:
                output = self.autoNonNIBSLoop(params)
                self.result_ready.emit({
                    'Pulse Shape': params.pulseType,
                    'Pulse Width (µs)': params.pulseWidth * 1000,
                    'Frequency (kHz)': 1 / params.ipi,
                    'Pulse Spacing (µs)': params.ipi * 1000,
                    '# of Pulses': params.numPulse,
                    'Coil Orientation (°)': params.angle,
                    'Pulse Length (µs)': params.pulseLength * 1000,
                    'Step Size (µs)': params.timeStep * 1000,
                    'Threshold Low': params.firedLow,
                    'Threshold High': params.firedHigh,
                    'Threshold Tolerance': params.firedTolerance,
                    'Coil Position x,y,z': ','.join(map(str, params.coilPos)),
                    'Neuron Position x,y,z': ','.join(map(str, params.neuronPos)),
                    'Neuron Orientation x,y,z': ','.join(map(str, params.neuronOrientation)),
                    'Neuron Axis x,y,z': ','.join(map(str, params.neuronAxis)),
                    'MagnE Normalized': output[6],
                    'Firing Threshold': output[1],
                    'MagnE (V/m)': output[6] * output[1],
                    'E1': output[3],
                    'E2': output[4],
                    'E3': output[5],
                    'Mean_ROI': output[2],
                })
        
        self.finished.emit()


    def autoNIBSLoop(self, params: paramSet) -> list[str]: 
        outFolder = 'simNibsPastOutput' + str(params.angle)
        trueOut = 'simNibsPastOutputs\\' + outFolder

        # Seeing if output has been created in previous run to save a sweet sweet 60 seconds or so every iteration
        # i promise it adds up
        # os.path.exists(trueOut)
        if os.path.exists(trueOut):
            self.progress.emit("Found pre-existing mesh at " + trueOut)
            meshPath = trueOut + '\\'
        else:
            self.progress.emit(f"Could not find pre-existing mesh, generating at {outFolder}")
            self.runSimNIBS(params)
            meshPath = 'simNibsOut\\'
        

        mean_val = [0, 0, 0, 0, 0, 0, 0]

        if self.findThreshold:
            self.progress.emit("Finding Threshold")

            # Running file to run neuron and matlab scripts
            self.progress.emit("\nRunning Neuron scripts...")
            if params.pulseType == "Rectangular":
                pulseShape = 5
            elif params.pulseType == "Biphasic":
                pulseShape = 4
            elif params.pulseType == "Monophasic":
                pulseShape = 2
            
            #calls TMS_Waveform modified to be a CLI tool
            subprocess.run(f"matlab -batch \"addpath('../Code/TMS_Waveform'); TMS_Waveform({params.timeStep}, {params.pulseWidth}, {pulseShape}, {params.ipi}, {params.numPulse}, {params.pulseLength})\"")
            
            #os.system('hocScript.ps1 ' + meshPath)
            nrnloc = f"{params.neuronPos[0]},{params.neuronPos[1]},{params.neuronPos[2]}"
            nrnaxs = f"{params.neuronAxis[0]},{params.neuronAxis[1]},{params.neuronAxis[2]}"
            nrnori = f"{params.neuronOrientation[0]},{params.neuronOrientation[1]},{params.neuronOrientation[2]}"

            p = subprocess.Popen(["powershell.exe", os.getcwd() + "\\hocScript.ps1", "-meshpath", meshPath, "-nrnloc", f"{nrnloc} -nrnaxs {nrnaxs} -nrnori {nrnori}"], stdout=sys.stdout)
            p.communicate()
            self.progress.emit("Done!")

            self.progress.emit("\nRunning BeNeMo...")
            # print(params.firedLow)
            # print(params.firedHigh)
            # print(params.firedTolerance)
            fired = checkFired(params.firedLow, params.firedHigh, params.firedTolerance)


            #making output
            mean_val = self.formatOutput(params.angle, fired)

            # Cleanup
        os.system("taskkill /f /im gmsh.exe")
        if os.path.exists('simNibsOut\\'):
            #os.rename('simNibsOut', outFolder)
            shutil.move('simNibsOut', os.path.join('simNibsPastOutputs', outFolder))
        for f in glob.glob("results*.txt"): # Globbin time
            os.remove(f)

        return mean_val


    def autoNonNIBSLoop(self, params: paramSet) -> list[str]: 
        self.progress.emit("Finding Threshold")
        # Running file to run neuron and matlab scripts
        self.progress.emit("\nRunning Neuron scripts...")
        if params.pulseType == "Rectangular":
            pulseShape = 5
        elif params.pulseType == "Biphasic":
            pulseShape = 4
        elif params.pulseType == "Monophasic":
            pulseShape = 2
        
        #calls TMS_Waveform modified to be a CLI tool
        subprocess.run(f"matlab -batch \"addpath('../Code/TMS_Waveform'); TMS_Waveform({params.timeStep}, {params.pulseWidth}, {pulseShape}, {params.ipi}, {params.numPulse}, {params.pulseLength})\"")
        self.progress.emit("\nRunning BeNeMo...")
        # print(params.firedLow)
        # print(params.firedHigh)
        # print(params.firedTolerance)
        x = cos(radians(params.angle))
        y = sin(radians(params.angle))
        z = 0

        paramFile = r'..\Results\Neuron\params.txt'

        #File Sanity Check
        if (os.path.exists(paramFile)):
            os.remove (paramFile)
        
        if not (os.path.exists(r'..\Results\NEURON')):
            os.mkdir(r'..\Results\NEURON')
        
        shutil.copy('noNibsParams.txt', paramFile)

        with open(r"..\Results\Neuron\params.txt", 'r') as file:
            filedata = file.readlines()
        stowrited1 = 'EX ' + str(x) + '\n'
        stowrited2 = 'EY ' + str(y) + '\n'
        stowrited3 = 'EZ ' + str(z) + '\n'
        filedata[5] = stowrited1
        filedata[6] = stowrited2
        filedata[7] = stowrited3
        with open(r'..\Results\NEURON\params.txt','w') as file:#writes the new list to the same file
            file.writelines(filedata)
        
        fired = checkUniformFired(params.firedLow, params.firedHigh, params.firedTolerance)

        #making output
        mean_val = self.formatOutput(params.angle, fired)
        return mean_val


    def runSimNIBS(self, params: paramSet) -> None: 
         # Calculating direction reference coordinates
        self.progress.emit("Calculating Positions for angle " + str(params.angle))
        ref = [0, 13.58, -21]
        normal = [params.coilPos[i] - ref[i] for i in range(3)]
        rad = radians(params.angle)
        dx = sin(rad)
        dy = cos(rad)
        xd = params.coilPos[0] + dx
        yd = params.coilPos[1] + dy
        zd = params.coilPos[2] + (-normal[0] * (xd - params.coilPos[0]) - normal[1] * (yd - params.coilPos[1])) / normal[2] # Equation provided in simulation parameters doc, solved for z

        #xd, yd, zd = -47.43, 76.11, 58.35
        coilDirRef = [xd, yd, zd]
        self.progress.emit(coilDirRef)
        self.progress.emit("Done!")


        # SimNIBS code
        self.progress.emit("\nRunning SimNIBS...")
        s = sim_struct.SESSION()

        s.subpath = 'm2m_ernie'

        s.pathfem = 'simNibsOut\\'

        tmslist = s.add_tmslist()

        tmslist.fnamecoil = 'Magstim_70mm_Fig8.ccd'

        pos = tmslist.add_position()

        pos.centre = params.coilPos
        pos.pos_ydir = coilDirRef
        pos.distance = 2

        run_simnibs(s)

        self.progress.emit("Done!")


    def formatOutput(self, angle: float, fired: int) -> list[str]: 
        mean_val = [angle, fired]
        if self.simType == 1:
            with open('output.txt') as file:
                    mean_val+= [line.rstrip() for line in file]
        return mean_val