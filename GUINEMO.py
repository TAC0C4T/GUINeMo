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
        self.XLabel = QLabel("X")
        self.YLabel = QLabel("Y")
        self.ZLabel = QLabel("Z")
        
        self.addWidget(self.XLabel, 0, 0)
        self.addWidget(self.YLabel, 0, 1)
        self.addWidget(self.ZLabel, 0, 2)
        self.addWidget(self.XBox, 1, 0)
        self.addWidget(self.YBox, 1, 1)
        self.addWidget(self.ZBox, 1, 2)
    
    # Return all values as tuple because "you shouldn't access class variables without a getter method" -🤓
    # Actually it just makes getting the values shorter to write
    def getValue(self) -> tuple[int, int, int]:
        return (self.XBox.value(), self.YBox.value(), self.ZBox.value())
    
    def hide(self) -> None:
        self.XBox.hide()
        self.YBox.hide()
        self.ZBox.hide()
        self.XLabel.hide()
        self.YLabel.hide()
        self.ZLabel.hide()

    def show(self) -> None:
        self.XBox.show()
        self.YBox.show()
        self.ZBox.show()
        self.XLabel.show()
        self.YLabel.show()
        self.ZLabel.show()



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
        self.pulseWidth = pulseWidth / 1000
        self.pulseLength = pulseLength / 1000
        self.ipi = ipi / 1000
        self.numPulse = numPulse
        self.pulseType = pulseType
        self.neuronPos = list(neuronPos)
        self.neuronOrientation = list(neuronOrientation)
        self.coilPos = list(coilPos)
        self.timeStep = timeStep / 1000
        self.firedLow = firedLow
        self.firedHigh = firedHigh
        self.firedTolerance = firedTolerance
        self.neuronAxis = list(neuronAxis)


class paramSetUniform:
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
            firedTolerance: int,):
        self.angle = angle
        self.pulseWidth = pulseWidth / 1000
        self.pulseLength = pulseLength / 1000
        self.ipi = ipi / 1000
        self.numPulse = numPulse
        self.pulseType = pulseType
        self.timeStep = timeStep / 1000
        self.firedLow = firedLow
        self.firedHigh = firedHigh
        self.firedTolerance = firedTolerance



# Main window
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


        self.simList = QTextEdit()
        self.simList.setAcceptRichText(False) # Disables formatting when copy-pasting
        self.textLayout = QVBoxLayout()
        self.textLayout.addWidget(QLabel("You can copy and paste from excel parameters here!"))
        self.boxLabels = QLabel("Pulse Type           Pulse Width        Frequency          IPI                     # Pulse             Angle                    Pulse Length      Step Size            Threshold Low    Threshold High   Tolerance            Coil Position                    Neuron Position      Neuron Orientation     Neuron Axis      ")
        self.textLayout.addWidget(self.boxLabels)
        self.textLayout.addWidget(self.simList)
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
        if type == 2:
            for element in self.simNIBSInputs:
                element.hide()
            self.angleMinLabel.setText("E-Field Angle Minimum (for only 1 angle put angle in this box, leave others blank)")
            self.angleMaxLabel.setText("E-Field Angle Maximum")
            self.angleStepLabel.setText("E-Field Angle Step")
            self.boxLabels.setText("Pulse Type           Pulse Width        Frequency          IPI                     # Pulse             Angle                    Pulse Length      Step Size            Threshold Low    Threshold High   Tolerance")




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

    # Called by runSims()
    # Turns text box contents into list of paramSets 
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
    
        
    # Called by pulseWidthBox
    # Updates pulseLengthBox to be 2x the width
    def updateLength(self):
        self.pulseLengthBox.setValue(self.pulseWidthBox.value() * 2)


    # Called by runButton
    # This is just the BeNeMo file copy pasted pretty much
    def runSims(self):
        data = self.simList.toPlainText()
        print(data)
        data = self.objectify(data)
        # Sanity checks. Code may work without this
        if os.path.isfile('output.csv'):
            os.remove('output.csv')

        if os.path.exists('simNibsOut\\'):
            rmtree('simNibsOut\\')

        if not os.path.exists('simNibsPastOutputs'):
            os.mkdir('simNibsPastOutputs')

        outputs = []
        if self.setSimType == 1:
            for params in data:
                outputs.append(self.autoNIBSLoop(params))
        elif self.setSimType == 2:
            for params in data:
                outputs.append(self.autoNonNIBSLoop(params))

        with open('output.csv', 'w', newline='') as csvfile:
            if self.setSimType == 1:
                fieldnames = [
                    'Pulse Shape', 'Pulse Width (µs)', 'Frequency (kHz)', 'Pulse Spacing (µs)', '# of Pulses',
                    'Coil Orientation (°)', 'Pulse Length (µs)', 'Step Size (µs)',
                    'Threshold Low', 'Threshold High', 'Threshold Tolerance',
                    'Coil Position x,y,z', 'Neuron Position x,y,z',
                    'Neuron Orientation x,y,z', 'Neuron Axis x,y,z',
                    'MagnE', 'Firing Threshold', 'E1', 'E2', 'E3', 'Mean_ROI',
                ]
            elif self.setSimType == 2:
                fieldnames = [
                    'Pulse Shape', 'Pulse Width (µs)', 'Frequency (kHz)', 'Pulse Spacing (µs)', '# of Pulses',
                    'Coil Orientation (°)', 'Pulse Length (µs)', 'Step Size (µs)',
                    'Threshold Low', 'Threshold High', 'Threshold Tolerance',
                    'MagnE', 'Firing Threshold', 'E1', 'E2', 'E3', 'Mean_ROI',
                ]


            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            

            if self.setSimType == 1:
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
                        'E1': row[3],
                        'E2': row[4],
                        'E3': row[5],
                        'Mean_ROI': row[2],
                    })
            elif self.setSimType == 2:
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
                        'MagnE': row[6],
                        'Firing Threshold': row[1],
                        'E1': row[3],
                        'E2': row[4],
                        'E3': row[5],
                        'Mean_ROI': row[2],
                    })

    
    # Runs SimNIBS
    # Called by autoNIBSLoop
    def runSimNIBS(self, params: paramSet) -> None:
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

        #xd, yd, zd = -47.43, 76.11, 58.35
        coilDirRef = [xd, yd, zd]
        print(coilDirRef)
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


    def formatOutput(self, angle: float, fired: int) -> list[str]:
        mean_val = [angle, fired]
        with open('output.txt') as file:
                mean_val+= [line.rstrip() for line in file]
        return mean_val
    
    def autoNonNIBSLoop(self, params: paramSet) -> list[str]:
        print("Finding Threshold")
        # Running file to run neuron and matlab scripts
        print("\nRunning Neuron scripts...")
        if params.pulseType == "Rectangular":
            pulseShape = 5
        else:
            pulseShape = 5
        
        #calls TMS_Waveform modified to be a CLI tool
        subprocess.run(f"matlab -batch \"addpath('../Code/TMS_Waveform'); TMS_Waveform({params.timeStep}, {params.pulseWidth}, {pulseShape}, {params.ipi}, {params.numPulse}, {params.pulseLength})\"")
        print("\nRunning BeNeMo...")
        print(params.firedLow)
        print(params.firedHigh)
        print(params.firedTolerance)
        x = cos(radians(params.angle))
        y = sin(radians(params.angle))
        z = 0
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
            print(f"Could not find pre-existing mesh, generating at {outFolder}")
            self.runSimNIBS(self, params)
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


        
        


# Runs PyQt
app = QApplication([])

window = MainWindow()
#window = QWidget()
window.show()

app.exec()