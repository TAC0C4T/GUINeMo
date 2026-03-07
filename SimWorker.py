from PyQt5.QtCore import QObject, QThread, pyqtSignal
import os
from rmtree import rmtree
import shutil
import csv

class SimWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(str)        # for sending log messages to the UI
    result_ready = pyqtSignal(dict)   # for sending each row's output back to UI

    #TODO OBJECTIFY PARAMS B4 INIT
    def __init__(self, data, sim_type, find_threshold): 
        super().__init__()
        self.data = data
        self.sim_type = sim_type
        self.findThreshold = find_threshold

    
    def run(self):                # contains the loop that's currently in runSims()

        data = self.data
        # Sanity checks. Code may work without this
        if os.path.isfile('output.csv'):
            os.remove('output.csv')

        if os.path.exists('simNibsOut\\'):
            rmtree('simNibsOut\\')

        if not os.path.exists('simNibsPastOutputs'):
            os.mkdir('simNibsPastOutputs')

        outputs = []
        fieldnames = []
        

        with open('output.csv', 'w', newline='', buffering=1) as csvfile:
            if self.setSimType == 1:
                fieldnames = [
                    'Pulse Shape', 'Pulse Width (µs)', 'Frequency (kHz)', 'Pulse Spacing (µs)', '# of Pulses',
                    'Coil Orientation (°)', 'Pulse Length (µs)', 'Step Size (µs)',
                    'Threshold Low', 'Threshold High', 'Threshold Tolerance',
                    'Coil Position x,y,z', 'Neuron Position x,y,z',
                    'Neuron Orientation x,y,z', 'Neuron Axis x,y,z',
                    'MagnE Normalized', 'Firing Threshold', 'MagnE (V/m)', 'E1', 'E2', 'E3', 'Mean_ROI',
                ]
            elif self.setSimType == 2:
                fieldnames = [
                    'Pulse Shape', 'Pulse Width (µs)', 'Frequency (kHz)', 'Pulse Spacing (µs)', '# of Pulses',
                    'Coil Orientation (°)', 'Pulse Length (µs)', 'Step Size (µs)',
                    'Threshold Low', 'Threshold High', 'Threshold Tolerance', 'Firing Threshold',
                ]


            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
        
        
        if self.setSimType == 1:
            for params in data:
                with open('output.csv', 'w', newline='', buffering=1) as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    output = self.autoNIBSLoop(params)
                    writer.writerow({
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
        elif self.setSimType == 2:
            for params in data:
                with open('output.csv', 'w', newline='', buffering=1) as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    output = self.autoNonNIBSLoop(params)
                    writer.writerow({
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
    def autoNIBSLoop(self, params): 
        outFolder = 'simNibsPastOutput' + str(params.angle)
        trueOut = 'simNibsPastOutputs\\' + outFolder

        # Seeing if output has been created in previous run to save a sweet sweet 60 seconds or so every iteration
        # i promise it adds up
        # os.path.exists(trueOut)
        if os.path.exists(trueOut):
            print("Found pre-existing mesh at " + trueOut)
            meshPath = trueOut + '\\'
        else:
            print(f"Could not find pre-existing mesh, generating at {outFolder}")
            self.runSimNIBS(params)
            meshPath = 'simNibsOut\\'
        

        mean_val = [0, 0, 0, 0, 0, 0, 0]

        if self.findThresholdBox.isChecked():
            print("Finding Threshold")

            # Running file to run neuron and matlab scripts
            print("\nRunning Neuron scripts...")
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
            print("Done!")

            print("\nRunning BeNeMo...")
            print(params.firedLow)
            print(params.firedHigh)
            print(params.firedTolerance)
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
    
    def autoNonNIBSLoop(self, params): ...
    def runSimNIBS(self, params): ...
    def formatOutput(self, angle, fired): ...