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
    QToolBar,
    QAction,
)
from customQTWidgets import angleBox, posTimeBox, positionBox
from PyQt5.QtCore import QObject, QThread, pyqtSignal

from SimWorker import SimWorker
from structs import paramSet, paramSetUniform
from simnibs import sim_struct, run_simnibs
from math import sin, cos, radians
import os
from checkfired import checkFired
from checkfiredUniform import checkUniformFired
from rmtree import rmtree
import csv
import shutil
import glob
import sys
import subprocess


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setSimType = 1
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
        self.angleMinLabel = QLabel("Coil Angle Minimum (for only 1 angle put angle in this box, leave others blank)")
        self.angleMaxLabel = QLabel("Coil Angle Maximum")
        self.angleStepLabel = QLabel("Coil Angle Step")
        self.inputLayout.addWidget(self.angleMinLabel)
        self.inputLayout.addWidget(self.angleMinBox)
        self.inputLayout.addWidget(self.angleMaxLabel)
        self.inputLayout.addWidget(self.angleMaxBox)
        self.inputLayout.addWidget(self.angleStepLabel)
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




        
        self.coilPosLabel = QLabel("Coil Position")
        #self.inputLayout.addWidget(self.coilPosLabel)
        #self.inputLayout.addLayout(self.coilPos)

        self.neuronPosLabel = QLabel("Neuron Position")
        #self.inputLayout.addWidget(self.neuronPosLabel)
        #self.inputLayout.addLayout(self.neuronPos)

        self.neuronOrientationLabel = QLabel("Neuron Orientation")
        #self.inputLayout.addWidget(self.neuronOrientationLabel)
        #self.inputLayout.addLayout(self.neuronOrientation)

        self.neuronAxisLabel = QLabel("Neuron Axis")
        #self.inputLayout.addWidget(self.neuronAxisLabel)
        #self.inputLayout.addLayout(self.neuronAxis)

        self.simNIBSInputs = [self.coilPosLabel,
                              self.coilPos,
                              self.neuronPosLabel, 
                              self.neuronPos, 
                              self.neuronOrientationLabel, 
                              self.neuronOrientation, 
                              self.neuronAxisLabel,
                              self.neuronAxis,
                              ]
        
        for item in self.simNIBSInputs:
            if isinstance(item, QLabel):
                self.inputLayout.addWidget(item)
            elif isinstance(item, positionBox):
                self.inputLayout.addLayout(item)
        
        
        


        self.addParamButton = QPushButton("Add Sim to Run")
        self.addParamButton.clicked.connect(self.addParams) # Runs function to add the info into the right box
        self.inputLayout.addWidget(self.addParamButton)
        
        self.inputLayout.addWidget(self.findThresholdBox)


        menu = self.menuBar()
        simType = menu.addMenu("&Sim Type")
        typeRealistic = QAction("Realistic", self)
        typeUniform = QAction("Uniform", self)
        typeRealistic.triggered.connect(lambda: self.setType(1))
        typeUniform.triggered.connect(lambda: self.setType(2))
        simType.addAction(typeRealistic)
        simType.addAction(typeUniform)

        #self.toolbar = QToolBar("")
        
        self.layout = QGridLayout()
        #self.screenLayout = QVBoxLayout()


        self.logBox = QTextEdit()
        self.simList = QTextEdit()
        self.simList.setAcceptRichText(False) # Disables formatting when copy-pasting
        self.textLayout = QVBoxLayout()
        self.textLayout.addWidget(QLabel("You can copy and paste from excel parameters here!"))
        self.boxLabels = QLabel("Pulse Type           Pulse Width        Frequency          IPI                     # Pulse             Angle                    Pulse Length      Step Size            Threshold Low    Threshold High   Tolerance            Coil Position                    Neuron Position      Neuron Orientation     Neuron Axis      ")
        self.textLayout.addWidget(self.boxLabels)
        self.textLayout.addWidget(self.simList)
        self.textLayout.addWidget(QLabel("Logs"))
        self.textLayout.addWidget(self.logBox)
        self.runButton = QPushButton("Run Simulations")
        self.textLayout.addWidget(self.runButton)
        self.runButton.clicked.connect(self.runSims) # Calls function to run all sims in list


        self.layout.addLayout(self.inputLayout, 0, 0)
        self.layout.addLayout(self.textLayout, 0, 1)

        #self.screenLayout.addLayout(self.layout)

        self.widget = QWidget()
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)


    # Called by simType
    def setType(self, type : int) -> None:
        self.setSimType = type
        if type == 1:
            for element in self.simNIBSInputs:
                element.show()
            self.angleMinLabel.setText("Coil Angle Minimum (for only 1 angle put angle in this box, leave others blank)")
            self.angleMaxLabel.setText("Coil Angle Maximum")
            self.angleStepLabel.setText("Coil Angle Step")
            self.boxLabels.setText("Pulse Type           Pulse Width        Frequency          IPI                     # Pulse             Angle                    Pulse Length      Step Size            Threshold Low    Threshold High   Tolerance            Coil Position                    Neuron Position      Neuron Orientation     Neuron Axis      ")
            self.findThresholdBox.show()
        if type == 2:
            for element in self.simNIBSInputs:
                element.hide()
            self.angleMinLabel.setText("E-Field Angle Minimum (for only 1 angle put angle in this box, leave others blank)")
            self.angleMaxLabel.setText("E-Field Angle Maximum")
            self.angleStepLabel.setText("E-Field Angle Step")
            self.boxLabels.setText("Pulse Type           Pulse Width        Frequency          IPI                     # Pulse             Angle                    Pulse Length      Step Size            Threshold Low    Threshold High   Tolerance")
            self.findThresholdBox.hide()


    # Called by addParamButton
    def addParams(self):
        for angle in range(self.angleMinBox.value(), self.angleMaxBox.value() if not self.angleMaxBox.value() <= self.angleMinBox.value() else self.angleMinBox.value() + 1, self.angleStepBox.value() if not self.angleStepBox.value() == 0 else 360):

            if self.setSimType == 1:
                self.simList.append(
                    self.pulseTypeSelector.currentText() + "\t" +
                    str(self.pulseWidthBox.value()) + "\t" + 
                    str((1 / (self.IPIBox.value() / 1000)) if not self.IPIBox.value() == 0 else 0) + "\t" +
                    str(self.IPIBox.value()) + "\t" +
                    str(self.numPulseBox.value()) + "\t" +
                    str(angle) + "\t" +
                    str(self.pulseLengthBox.value()) + "\t" +
                    str(self.timeStepBox.value()) + "\t" +
                    str(self.lowBox.value()) + "\t" +
                    str(self.highBox.value()) + "\t" +
                    str(self.toleranceBox.value()) + "\t" +
                    ','.join(map(str, self.coilPos.getValue())) + "\t" +
                    ','.join(map(str, self.neuronPos.getValue())) + "\t" +
                    ','.join(map(str, self.neuronOrientation.getValue())) + "\t" +
                    ','.join(map(str, self.neuronAxis.getValue()))
                )
            elif self.setSimType == 2:
                self.simList.append(
                    self.pulseTypeSelector.currentText() + "\t" +
                    str(self.pulseWidthBox.value()) + "\t" + 
                    str((1 / (self.IPIBox.value() / 1000)) if not self.IPIBox.value() == 0 else 0) + "\t" +
                    str(self.IPIBox.value()) + "\t" +
                    str(self.numPulseBox.value()) + "\t" +
                    str(angle) + "\t" +
                    str(self.pulseLengthBox.value()) + "\t" +
                    str(self.timeStepBox.value()) + "\t" +
                    str(self.lowBox.value()) + "\t" +
                    str(self.highBox.value()) + "\t" +
                    str(self.toleranceBox.value())
                )


    # Called by pulseWidthBox
    # Updates pulseLengthBox to be 2x the width
    def updateLength(self):
        self.pulseLengthBox.setValue(self.pulseWidthBox.value() * 2)

    def objectify(self, data: str) -> list[paramSet]:
        data = data.splitlines()
        data = map(lambda x : x.split("\t"), data)
        
        simParams = []

        if self.setSimType == 1:
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
        elif self.setSimType == 2:
            for list in data:
                simParams.append(paramSetUniform(int(list[5]), 
                                        float(list[1]), 
                                        float(list[6]), 
                                        float(list[3]), 
                                        int(list[4]), 
                                        list[0], 
                                        float(list[7]), 
                                        int(list[8]), 
                                        int(list[9]), 
                                        int(list[10]), 
                                        ))
            return simParams

    def runSims(self): 
        data = self.objectify(self.simList.toPlainText())

        self.runButton.setEnabled(False)

        self.thread = QThread()
        self.worker = SimWorker(data, self.setSimType, self.findThresholdBox.isChecked())
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        
        self.worker.progress.connect(self.onProgress)
        self.worker.result_ready.connect(self.onResultReady)
        self.worker.finished.connect(self.onFinished)
        
        self.thread.start()
                                      

    def onProgress(self, msg):    # receives log
        self.logBox.append(msg)


    def onResultReady(self, row):
        with open('output.csv', 'a', newline='', buffering=1) as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.fieldnames)
            writer.writerow(row)


    def onFinished(self):
        self.runButton.setEnabled(True)

# Runs PyQt
app = QApplication([])

window = MainWindow()
#window = QWidget()
window.show()

app.exec()