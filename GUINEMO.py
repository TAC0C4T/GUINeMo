from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import (
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
    def __init__(self, angle: int, pulseWidth: float, pulseLength: float, ipi: float, numPulse: int, pulseType, neuronPos, neuronOrientation):
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
    
    def runSims(self):
        data = self.simList.toPlainText()
        data = data.splitlines()
        data = map(lambda x : x.split("\t"), data)
        
        simParams = []

        for list in data:
            simParams.append(paramSet(int(list[5]), float(list[1]), float(list[6]), float(list[3]), int(list[4]), list[0], None, None))

        for row in list:
            print(row)
    
    def autoNIBSLoop():

        
        



app = QApplication([])

window = MainWindow()
#window = QWidget()
window.show()

app.exec()