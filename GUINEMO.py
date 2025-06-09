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

class angleBox(QSpinBox):
    def __init__(self):
        super().__init__()
        self.setMinimum(0)
        self.setMaximum(360)
        self.setSuffix("°")

class posTimeBox(QDoubleSpinBox):
    def __init__(self):
        super().__init__()
        self.setMinimum(0)
        self.setSuffix("µs")

class paramSet:
    def __init__(self, angle: int, pulseWidth: float, pulseLength: float, ipi: float, numPulse: int, pulseType: str, neuronPos, neuronOrientation):
        self.angle = angle
        self.pulseWidth = pulseWidth
        self.pulseLength = pulseLength
        self.ipi = ipi
        self.numPulse = numPulse
        self.pulseType = pulseType
        self.neuronPos = neuronPos
        self.neuronOrientation = neuronOrientation


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
        self.IPIBox = posTimeBox()
        self.numPulseBox = QSpinBox()
        self.numPulseBox.setMinimum(1)

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


        self.addParamButton = QPushButton("Add Sim to Run")
        self.addParamButton.clicked.connect(self.addParams)
        self.inputLayout.addWidget(self.addParamButton)


        
        
        self.layout = QGridLayout()

        self.simList = QTextEdit()
        self.simList.setAcceptRichText(False)
        self.textLayout = QVBoxLayout()
        self.textLayout.addWidget(QLabel("You can copy and paste from excel parameters here!"))
        #self.textLayout.addWidget(QLabel("Pulse Type\tPulse Width\tFrequency\tIPI\t# Pulses\tAngle\tPulse Length"))
        self.textLayout.addWidget(self.simList)
        self.runButton = QPushButton("Run Simulations")
        self.textLayout.addWidget(self.runButton)
        self.runButton.clicked.connect(self.runSims)


        self.layout.addLayout(self.inputLayout, 0, 0)
        self.layout.addLayout(self.textLayout, 0, 1)

        self.widget = QWidget()
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

    def addParams(self):
        for angle in range(self.angleMinBox.value(), self.angleMaxBox.value() if not self.angleMaxBox.value() <= self.angleMinBox.value() else self.angleMinBox.value() + 1, self.angleStepBox.value() if not self.angleStepBox.value() == 0 else 360):

            self.simList.append(
                self.pulseTypeSelector.currentText() + "\t" +
                str(self.pulseWidthBox.value()) + "\t" + 
                str((1 / self.IPIBox.value()) if not self.IPIBox.value() == 0 else 0) + "\t" +
                str(self.IPIBox.value()) + "\t" +
                str(self.numPulseBox.value()) + "\t" +
                str(angle) + "\t" +
                str(self.pulseLengthBox.value())

            )


    def objectify(self, data: str) -> list[paramSet]:
        data = data.splitlines()
        data = map(lambda x : x.split("\t"), data)
        
        simParams = []

        for list in data:
            simParams.append(paramSet(int(list[5]), float(list[1]), float(list[6]), float(list[3]), int(list[4]), list[0], None, None))
        return simParams


    
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
        for row in outputs:
            print(row)
    
    
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
        subprocess.run(f"matlab -batch \"addpath('../Code/TMS_Waveform'); TMS_Waveform({.005}, {params.pulseWidth}, {pulseShape}, {params.ipi}, {params.numPulse})\"")
        #os.system('hocScript.ps1 ' + meshPath)
        p = subprocess.Popen(["powershell.exe", os.getcwd() + "\\hocScript.ps1", meshPath], stdout=sys.stdout)
        p.communicate()
        print("Done!")

        print("\nRunning BeNeMo...")
        fired = checkFired()


        #making csv
        mean_val= [fired]
        with open('output.txt') as file:
            mean_val+= [line.rstrip() for line in file]

        # Cleanup
        if os.path.exists('simNibsOut\\'):
            os.rename('simNibsOut', outFolder)
            shutil.move(outFolder, 'simNibsPastOutputs')
        for f in glob.glob("results*.txt"): # Globbin time
            os.remove(f)

        return mean_val


        
        



app = QApplication([])

window = MainWindow()
#window = QWidget()
window.show()

app.exec()