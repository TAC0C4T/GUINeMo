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

# Each object of this class is a single simulation
class paramSet:
    def __init__(self, angle: int, pulseWidth: float, pulseLength: float, ipi: float, numPulse: int, pulseType: str, timeStep: float, neuronPos, neuronOrientation):
        self.angle = angle
        self.pulseWidth = pulseWidth
        self.pulseLength = pulseLength
        self.ipi = ipi
        self.numPulse = numPulse
        self.pulseType = pulseType
        self.neuronPos = neuronPos
        self.neuronOrientation = neuronOrientation
        self.timeStep = timeStep

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

        self.pulseTypeSelector = QComboBox()
        self.pulseTypeSelector.addItems(["Monophasic", "Biphasic", "Rectangular"])


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


        self.addParamButton = QPushButton("Add Sim to Run")
        self.addParamButton.clicked.connect(self.addParams) # Runs function to add the info into the right box
        self.inputLayout.addWidget(self.addParamButton)


        
        
        self.layout = QGridLayout()

        self.simList = QTextEdit()
        self.simList.setAcceptRichText(False) # Disables formatting when copy-pasting
        self.textLayout = QVBoxLayout()
        self.textLayout.addWidget(QLabel("You can copy and paste from excel parameters here!"))
        #self.textLayout.addWidget(QLabel("Pulse Type\tPulse Width\tFrequency\tIPI\t# Pulses\tAngle\tPulse Length"))
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
                str(self.timeStepBox.value() / 1000)

            )

    # Called by runSims()
    # Turns text box contents into list of paramSets 
    def objectify(self, data: str) -> list[paramSet]:
        data = data.splitlines()
        data = map(lambda x : x.split("\t"), data)
        
        simParams = []

        for list in data:
            simParams.append(paramSet(int(list[5]), float(list[1]), float(list[6]), float(list[3]), int(list[4]), list[0], float(list[7]), None, None))
        return simParams
    
    # Called by pulseWidthBox
    # Updates pulseLengthBox to be 2x the width
    def updateLength(self):
        self.pulseLengthBox.setValue(self.pulseWidthBox.value() * 2)


    # Called by runButton
    # This is just the BeNeMo
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
            outputs.append(self.autoNIBSLoop(params, [-47.79, 74.76, 58.94]))

        with open('output.csv', 'w', newline='') as csvfile:
            fieldnames = ['angle', 'fired', 'Mean_ROI', 'E1', 'E2', 'E3', 'MagnE']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in outputs:
                writer.writerow({'angle': row[0], 'fired': row[1], 'Mean_ROI': row[2], 'E1': row[3], 'E2': row[4], 'E3': row[5], 'MagnE': row[6]})
    
    
    def autoNIBSLoop(self, params: paramSet, coilPos: tuple[int, int, int]) -> list[str]:
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
            normal = [coilPos[i] - ref[i] for i in range(3)]
            rad = radians(params.angle)
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
        if params.pulseType == "Rectangular":
            pulseShape = 5
        else:
            pulseShape = 5
        
        #calls TMS_Waveform modified to be a CLI tool
        subprocess.run(f"matlab -batch \"addpath('../Code/TMS_Waveform'); TMS_Waveform({params.timeStep}, {params.pulseWidth}, {pulseShape}, {params.ipi}, {params.numPulse}, {params.pulseLength})\"")
        
        #os.system('hocScript.ps1 ' + meshPath)
        p = subprocess.Popen(["powershell.exe", os.getcwd() + "\\hocScript.ps1", meshPath], stdout=sys.stdout)
        p.communicate()
        print("Done!")

        print("\nRunning BeNeMo...")
        fired = checkFired()


        #making csv
        mean_val= [params.angle, fired]
        with open('output.txt') as file:
            mean_val+= [line.rstrip() for line in file]

        # Cleanup
        if os.path.exists('simNibsOut\\'):
            os.rename('simNibsOut', outFolder)
            shutil.move(outFolder, 'simNibsPastOutputs')
        for f in glob.glob("results*.txt"): # Globbin time
            os.remove(f)

        return mean_val


        
        


# Runs PyQt
app = QApplication([])

window = MainWindow()
#window = QWidget()
window.show()

app.exec()