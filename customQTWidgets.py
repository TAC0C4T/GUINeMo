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