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
    def runSims(self): ...            # now just sets up the QThread, creates SimWorker,
                                      # moves worker to thread, connects signals, starts thread

    def onProgress(self, msg): ...    # slot: receives log messages, appends to a log widget
    def onResultReady(self, row): ... # slot: receives each result dict, writes it to the CSV
    def onFinished(self): ...         # slot: re-enables the run button, cleans up thread ref