from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QDoubleSpinBox,
    QComboBox,
    QSpinBox,
    QVBoxLayout,
    QGridLayout,
    QLabel,
    QWidget,
    QTextEdit,
    QCheckBox,
)
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


# Set up class for angles since they all have the same limits
class angleBox(QSpinBox):
    def __init__(self):
        super().__init__()
        self.setMinimum(0)
        self.setMaximum(360)
        self.setSuffix("°")

# Set up class for time boxes since they all have the same limits
class posTimeBox(QDoubleSpinBox):
    def __init__(self):
        super().__init__()
        self.setMinimum(0)
        self.setMaximum(1000)
        self.setSuffix("µs")

# Set up class for positioning because they all have the same parameters
class positionBox(QGridLayout):
    def __init__(self):
        super().__init__()
        self.XBox = QDoubleSpinBox()
        self.XBox.setMinimum(-1000)
        self.XBox.setMaximum(1000)
        self.YBox = QDoubleSpinBox()
        self.YBox.setMinimum(-1000)
        self.YBox.setMaximum(1000)
        self.ZBox = QDoubleSpinBox()
        self.ZBox.setMinimum(-1000)
        self.ZBox.setMaximum(1000)
        
        self.addWidget(QLabel("X"), 0, 0)
        self.addWidget(QLabel("Y"), 0, 1)
        self.addWidget(QLabel("Z"), 0, 2)
        self.addWidget(self.XBox, 1, 0)
        self.addWidget(self.YBox, 1, 1)
        self.addWidget(self.ZBox, 1, 2)
    
    # Return all values as tuple because "you shouldn't access class variables without a getter method" -🤓
    # Actually it just makes getting the values shorter to write
    def getValue(self) -> tuple[int, int, int]:
        return (self.XBox.value(), self.YBox.value(), self.ZBox.value())


# Each object of this class is a single simulation
class paramSet:
    def __init__(self,
                angle: int, 
                pulseWidth: float, 
                pulseLength: float, 
                ipi: float, 
                numPulse: int, 
                pulseType: str, 
                timeStep: float, 
                firedLow: int, 
                firedHigh: int, 
                firedTolerance: int, 
                neuronPos: tuple[float, float, float], 
                neuronOrientation: tuple[float, float, float], 
                coilPos: tuple[float, float, float], 
                neuronAxis: tuple[float, float, float]):
        self.angle = angle
        self.pulseWidth = pulseWidth
        self.pulseLength = pulseLength
        self.ipi = ipi
        self.numPulse = numPulse
        self.pulseType = pulseType
        self.neuronPos = list(neuronPos)
        self.neuronOrientation = list(neuronOrientation)
        self.coilPos = list(coilPos)
        self.timeStep = timeStep
        self.firedLow = firedLow
        self.firedHigh = firedHigh
        self.firedTolerance = firedTolerance
        self.neuronAxis = list(neuronAxis)


# Main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("GUINEMO")
        self.inputLayout = QVBoxLayout()

        self.angleMinBox = angleBox()
        self.angleMaxBox = angleBox()
        self.angleStepBox = angleBox()

        self.pulseWidthBox = posTimeBox()
        self.pulseLengthBox = posTimeBox()
        self.pulseWidthBox.valueChanged.connect(self.updateLength) # Calls function to set length to 2x width by default
        self.IPIBox = posTimeBox()
        self.numPulseBox = QSpinBox()
        self.numPulseBox.setMinimum(1)
        self.timeStepBox = posTimeBox()
        self.timeStepBox.setValue(5)
        self.lowBox = QSpinBox()
        self.lowBox.setMinimum(0)
        self.lowBox.setMaximum(10000)
        self.highBox = QSpinBox()
        self.highBox.setMinimum(0)
        self.highBox.setMaximum(10000)
        self.highBox.setValue(1000)
        self.toleranceBox = QSpinBox()
        self.toleranceBox.setMinimum(0)
        self.toleranceBox.setValue(2)

        self.pulseTypeSelector = QComboBox()
        self.pulseTypeSelector.addItems(["Monophasic", "Biphasic", "Rectangular"])


        self.coilPos = positionBox()
        defaultCoil = (-47.79, 74.76, 58.94)
        self.coilPos.XBox.setValue(defaultCoil[0])
        self.coilPos.YBox.setValue(defaultCoil[1])
        self.coilPos.ZBox.setValue(defaultCoil[2])

        self.neuronPos = positionBox()
        defaultPos = (-41.2, 71.4, 55.3)
        self.neuronPos.XBox.setValue(defaultPos[0])
        self.neuronPos.YBox.setValue(defaultPos[1])
        self.neuronPos.ZBox.setValue(defaultPos[2])
        
        self.neuronAxis = positionBox()
        defaultAxs = (0, 1, 0)
        self.neuronAxis.XBox.setValue(defaultAxs[0])
        self.neuronAxis.YBox.setValue(defaultAxs[1])
        self.neuronAxis.ZBox.setValue(defaultAxs[2])

        self.neuronOrientation = positionBox()
        defaultOrientation = (1, 0, 0)
        self.neuronOrientation.XBox.setValue(defaultOrientation[0])
        self.neuronOrientation.YBox.setValue(defaultOrientation[1])
        self.neuronOrientation.ZBox.setValue(defaultOrientation[2])


        self.findThresholdBox = QCheckBox("Find firing threshold (Disable to just generate SimNIBS files)")
        self.findThresholdBox.setChecked(True)





        
        # Adding elements to GUI
        self.inputLayout.addWidget(QLabel("Coil Angle Minimum (for only 1 angle put angle in this box, leave others blank)"))
        self.inputLayout.addWidget(self.angleMinBox)
        self.inputLayout.addWidget(QLabel("Coil Angle Maximum"))
        self.inputLayout.addWidget(self.angleMaxBox)
        self.inputLayout.addWidget(QLabel("Coil Angle Step"))
        self.inputLayout.addWidget(self.angleStepBox)


        self.inputLayout.addWidget(QLabel("Pulse Width"))
        self.inputLayout.addWidget(self.pulseWidthBox)
        self.inputLayout.addWidget(QLabel("Pulse Length"))
        self.inputLayout.addWidget(self.pulseLengthBox)
        self.inputLayout.addWidget(QLabel("Inter-Pulse-Interval"))
        self.inputLayout.addWidget(self.IPIBox)


        self.inputLayout.addWidget(QLabel("Pulse Type"))
        self.inputLayout.addWidget(self.pulseTypeSelector)
        self.inputLayout.addWidget(QLabel("Number of Pulses"))
        self.inputLayout.addWidget(self.numPulseBox)
        self.inputLayout.addWidget(QLabel("Time Step"))
        self.inputLayout.addWidget(self.timeStepBox)

        self.inputLayout.addWidget(QLabel("Threshold search parameters"))
        self.inputLayout.addWidget(QLabel("Low"))
        self.inputLayout.addWidget(self.lowBox)
        self.inputLayout.addWidget(QLabel("High"))
        self.inputLayout.addWidget(self.highBox)
        self.inputLayout.addWidget(QLabel("Tolerance"))
        self.inputLayout.addWidget(self.toleranceBox)


        self.inputLayout.addWidget(QLabel("Coil Position"))
        self.inputLayout.addLayout(self.coilPos)

        self.inputLayout.addWidget(QLabel("Neuron Position"))
        self.inputLayout.addLayout(self.neuronPos)

        self.inputLayout.addWidget(QLabel("Neuron Orientation"))
        self.inputLayout.addLayout(self.neuronOrientation)

        self.inputLayout.addWidget(QLabel("Neuron Axis"))
        self.inputLayout.addLayout(self.neuronAxis)


        self.addParamButton = QPushButton("Add Sim to Run")
        self.addParamButton.clicked.connect(self.addParams) # Runs function to add the info into the right box
        self.inputLayout.addWidget(self.addParamButton)
        
        self.inputLayout.addWidget(self.findThresholdBox)


        
        
        self.layout = QGridLayout()

        self.simList = QTextEdit()
        self.simList.setAcceptRichText(False) # Disables formatting when copy-pasting
        self.textLayout = QVBoxLayout()
        self.textLayout.addWidget(QLabel("You can copy and paste from excel parameters here!"))
        self.textLayout.addWidget(QLabel("Pulse Type           Pulse Width        Frequency          IPI                     # Pulse             Angle                    Pulse Length      Step Size            Threshold Low    Threshold High   Tolerance            Coil Position                    Neuron Position      Neuron Orientation     Neuron Axis      "))
        self.textLayout.addWidget(self.simList)
        self.runButton = QPushButton("Run Simulations")
        self.textLayout.addWidget(self.runButton)
        self.runButton.clicked.connect(self.runSims) # Calls function to run all sims in list


        self.layout.addLayout(self.inputLayout, 0, 0)
        self.layout.addLayout(self.textLayout, 0, 1)

        self.widget = QWidget()
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

    # Called by addParamButton
    def addParams(self):
        for angle in range(self.angleMinBox.value(), self.angleMaxBox.value() if not self.angleMaxBox.value() <= self.angleMinBox.value() else self.angleMinBox.value() + 1, self.angleStepBox.value() if not self.angleStepBox.value() == 0 else 360):

            self.simList.append(
                self.pulseTypeSelector.currentText() + "\t" +
                str(self.pulseWidthBox.value() / 1000) + "\t" + 
                str((1 / (self.IPIBox.value() / 1000)) if not self.IPIBox.value() == 0 else 0) + "\t" +
                str(self.IPIBox.value() / 1000) + "\t" +
                str(self.numPulseBox.value()) + "\t" +
                str(angle) + "\t" +
                str(self.pulseLengthBox.value() / 1000) + "\t" +
                str(self.timeStepBox.value() / 1000) + "\t" +
                str(self.lowBox.value()) + "\t" +
                str(self.highBox.value()) + "\t" +
                str(self.toleranceBox.value()) + "\t" +
                ','.join(map(str, self.coilPos.getValue())) + "\t" +
                ','.join(map(str, self.neuronPos.getValue())) + "\t" +
                ','.join(map(str, self.neuronOrientation.getValue())) + "\t" +
                ','.join(map(str, self.neuronAxis.getValue()))

            )

    # Called by runSims()
    # Turns text box contents into list of paramSets 
    def objectify(self, data: str) -> list[paramSet]:
        data = data.splitlines()
        data = map(lambda x : x.split("\t"), data)
        
        simParams = []

        for list in data:
            simParams.append(paramSet(int(list[5]), 
                                      float(list[1]), 
                                      float(list[6]), 
                                      float(list[3]), 
                                      int(list[4]), 
                                      list[0], 
                                      float(list[7]), 
                                      int(list[8]), 
                                      int(list[9]), 
                                      int(list[10]), 
                                      map(float, tuple(list[12].split(','))), 
                                      map(float, tuple(list[13].split(','))), 
                                      map(float, tuple(list[11].split(','))), 
                                      map(float, tuple(list[14].split(','))),
                                      ))
        return simParams
    
    # Called by pulseWidthBox
    # Updates pulseLengthBox to be 2x the width
    def updateLength(self):
        self.pulseLengthBox.setValue(self.pulseWidthBox.value() * 2)


    # Called by runButton
    # This is just the BeNeMo file copy pasted pretty much
    def runSims(self):
        data = self.simList.toPlainText()
        data = self.objectify(data)
        # Sanity checks. Code may work without this
        if os.path.isfile('output.csv'):
            os.remove('output.csv')

        if os.path.exists('simNibsOut\\'):
            rmtree('simNibsOut\\')

        if not os.path.exists('simNibsPastOutputs'):
            os.mkdir('simNibsPastOutputs')

        outputs = []
        for params in data:
            outputs.append(self.autoNIBSLoop(params))

        with open('output.csv', 'w', newline='') as csvfile:
            fieldnames = [
                'Pulse Shape', 'Pulse Width (µs)', 'Frequency (kHz)', 'Pulse Spacing (µs)', '# of Pulses',
                'Coil Orientation (°)', 'Pulse Length (µs)', 'Step Size (µs)',
                'Threshold Low', 'Threshold High', 'Threshold Tolerance',
                'Coil Position x,y,z', 'Neuron Position x,y,z',
                'Neuron Orientation x,y,z', 'Neuron Axis x,y,z',
                'MagnE', 'Firing Threshold'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for row, params in zip(outputs, data):
                writer.writerow({
                    'Pulse Shape': params.pulseType,
                    'Pulse Width (µs)': params.pulseWidth,
                    'Frequency (kHz)': 1 / params.ipi,
                    'Pulse Spacing (µs)': params.ipi,
                    '# of Pulses': params.numPulse,
                    'Coil Orientation (°)': params.angle,
                    'Pulse Length (µs)': params.pulseLength,
                    'Step Size (µs)': params.timeStep,
                    'Threshold Low': params.firedLow,
                    'Threshold High': params.firedHigh,
                    'Threshold Tolerance': params.firedTolerance,
                    'Coil Position x,y,z': ','.join(map(str, params.coilPos)),
                    'Neuron Position x,y,z': ','.join(map(str, params.neuronPos)),
                    'Neuron Orientation x,y,z': ','.join(map(str, params.neuronOrientation)),
                    'Neuron Axis x,y,z': ','.join(map(str, params.neuronAxis)),
                    'MagnE': row[6],
                    'Firing Threshold': row[1],
                })
    
    
    def autoNIBSLoop(self, params: paramSet) -> list[str]:
        outFolder = 'simNibsPastOutput' + str(params.angle)
        trueOut = 'simNibsPastOutputs\\' + outFolder

        # Seeing if output has been created in previous run to save a sweet sweet 60 seconds or so every iteration
        # i promise it adds up
        # os.path.exists(trueOut)
        if os.path.exists(trueOut):
            print("Found pre-existing mesh at " + trueOut)
            meshPath = trueOut + '\\'
        else:

            # Calculating direction reference coordinates
            print("Calculating Positions for angle " + str(params.angle))
            ref = [0, 13.58, -21]
            normal = [params.coilPos[i] - ref[i] for i in range(3)]
            rad = radians(params.angle)
            dx = sin(rad)
            dy = cos(rad)
            xd = params.coilPos[0] + dx
            yd = params.coilPos[1] + dy
            zd = params.coilPos[2] + (-normal[0] * (xd - params.coilPos[0]) - normal[1] * (yd - params.coilPos[1])) / normal[2] # Equation provided in simulation parameters doc, solved for z

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

            pos.centre = params.coilPos
            pos.pos_ydir = coilDirRef
            pos.distance = 2

            run_simnibs(s)

            print("Done!")
            meshPath = 'simNibsOut\\'
        

        mean_val = [0, 0, 0, 0, 0, 0, 0]

        if self.findThresholdBox.isChecked():
            print("Finding Threshold")

            # Running file to run neuron and matlab scripts
            print("\nRunning Neuron scripts...")
            if params.pulseType == "Rectangular":
                pulseShape = 5
            else:
                pulseShape = 5
            
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


            #making csv
            mean_val= [params.angle, fired]
            with open('output.txt') as file:
                mean_val+= [line.rstrip() for line in file]

        # Cleanup
        os.system("taskkill /f /im gmsh.exe")
        if os.path.exists('simNibsOut\\'):
            #os.rename('simNibsOut', outFolder)
            shutil.move('simNibsOut', os.path.join('simNibsPastOutputs', outFolder))
        for f in glob.glob("results*.txt"): # Globbin time
            os.remove(f)

        return mean_val


        
        


# Runs PyQt
app = QApplication([])

window = MainWindow()
#window = QWidget()
window.show()

app.exec()