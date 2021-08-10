from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtWidgets import QWidget, QPushButton, QLineEdit, QLabel,\
    QSpinBox, QGroupBox
from positionTrigger import PositionTriggerData, PositionTriggerWorker


class Port(QWidget):
    positionTriggerChangedSignal = pyqtSignal(object)

    def __init__(self, name, appendPortList, getTreadmillData, treadmill):
        super(Port, self).__init__()
        self.name = name
        self.treadmill = treadmill
        self.getTreadmillData = getTreadmillData
        self.positionTriggerData = PositionTriggerData(self)

        # create worker thread
        self.worker = PositionTriggerWorker(self.positionTriggerData)
        self.initThread()
        self.positionTriggerChangedSignal.connect(self.worker.updateTriggerInterval)

        # initialize UI elements
        self.label = QLabel(self.name)
        self.editLabel = QLineEdit()
        self.switchButton = QPushButton("OFF")
        self.editTriggerDuration = QSpinBox()
        self.pulseButton = QPushButton("Impulse")
        self.pulseRepetitionButton = QPushButton("Single Shot")
        self.editTriggerPosition = QSpinBox()
        self.editTriggerWindow = QSpinBox()
        self.editTriggerRetention = QSpinBox()
        self.setButton = QPushButton("Set")
        self.restoreButton = QPushButton("Restore")
        self.groupboxPositionTrigger = QGroupBox()
        self.pulseTimer = QTimer()

        # set parameters of UI elements
        self.setUIElements()

        # update and send data about port instance to main thread
        self.getPositionTriggerData()
        appendPortList(self.positionTriggerData)

        self.portDictionary = {
            "switchButton":        self.switchButton,
            "pulseButton":         self.pulseButton,
            "triggerDuration":     self.editTriggerDuration,
            "triggerPosition":     self.editTriggerPosition,
            "triggerWindow":       self.editTriggerWindow,
            "triggerRetention":    self.editTriggerRetention,
            "timer":               self.pulseTimer,
            "onString":            self.name,
            "offString":           self.name.lower()
        }

    def setUIElements(self):
        self.editLabel.setPlaceholderText("port " + self.name)

        self.switchButton.setStyleSheet("color: white;" "background-color: red")
        self.switchButton.setCheckable(True)
        self.switchButton.toggled.connect(self.portSwitchAction)
        self.pulseTimer.timeout.connect(lambda: self.switchButton.setChecked(False))

        self.editTriggerDuration.setAlignment(Qt.AlignRight)
        self.editTriggerDuration.setSuffix(" ms")
        self.editTriggerDuration.valueChanged.connect(self.getPulseDuration)

        self.pulseButton.clicked.connect(self.pulseSignalAction)

        self.pulseRepetitionButton.setCheckable(True)
        self.pulseRepetitionButton.setFocusPolicy(Qt.NoFocus)
        self.pulseRepetitionButton.toggled.connect(self.pulseRepetitionButtonAction)

        self.editTriggerPosition.setAlignment(Qt.AlignRight)
        self.editTriggerPosition.setSuffix(" ‰")
        self.editTriggerPosition.valueChanged.connect(
            lambda: self.valueChanged(self.editTriggerPosition, self.positionTriggerData.start))

        self.editTriggerWindow.setAlignment(Qt.AlignRight)
        self.editTriggerWindow.setSuffix(" ‰")
        self.editTriggerWindow.valueChanged.connect(
            lambda: self.valueChanged(self.editTriggerWindow, self.positionTriggerData.window))

        self.editTriggerRetention.setAlignment(Qt.AlignRight)
        self.editTriggerRetention.setSuffix(" ms")
        self.editTriggerRetention.valueChanged.connect(
            lambda: self.valueChanged(self.editTriggerRetention, self.positionTriggerData.retention))

        self.setButton.clicked.connect(self.setButtonAction)

        self.restoreButton.clicked.connect(self.restoreButtonAction)

        self.groupboxPositionTrigger.setCheckable(True)
        self.groupboxPositionTrigger.toggled.connect(self.groupboxToggleAction)
        self.groupboxPositionTrigger.setChecked(False)
        # self.enableChildrenWidgets(self.groupboxPositionTrigger)

    def initThread(self):
        self.positionTriggerData.thread = QThread(self)
        self.worker.moveToThread(self.positionTriggerData.thread)
        self.positionTriggerData.thread.started.connect(self.worker.process)
        self.worker.finished.connect(self.positionTriggerData.thread.quit)
        self.worker.triggerSignal.connect(self.pulseSignalAction)
        # self.worker.finished.connect(self.worker.deleteLater)
        # self.positionTriggerData.thread.finished.connect(self.positionTriggerData.thread.deleteLater)

    @staticmethod
    def initSingleSpinBox(widget, minv, maxv, val, step):
        widget.setRange(minv, maxv)
        widget.setValue(val)
        widget.setSingleStep(step)

    def initSpinBox(self):
        Port.initSingleSpinBox(self.editTriggerDuration, 100, 5000, 100, 100)
        Port.initSingleSpinBox(self.editTriggerPosition, 1, 1000, 500, 50)
        Port.initSingleSpinBox(self.editTriggerWindow, 0, 999, 100, 50)
        Port.initSingleSpinBox(self.editTriggerRetention, 50, 10000, 3000, 500)
        self.setButtonAction()

    def portSwitchAction(self, checked):
        if checked:
            self.switchButton.setText("ON")
            self.switchButton.setStyleSheet("color: white;"
                                            "background-color: green;")
            self.pulseButton.setDisabled(True)
            self.treadmill.writeData(self.portDictionary["onString"])
        else:
            self.switchButton.setText("OFF")
            self.switchButton.setStyleSheet("color: white;"
                                            "background-color: red;")
            self.pulseButton.setDisabled(False)
            self.pulseTimer.stop()
            self.treadmill.writeData(self.portDictionary["offString"])

    def pulseSignalAction(self):
        pulseInterval = self.editTriggerDuration.value()
        self.pulseTimer.start(pulseInterval)
        self.switchButton.setChecked(True)

    def pulseRepetitionButtonAction(self, checked):
        if checked:
            self.pulseRepetitionButton.setText("Continuous Shot")
            self.worker.setTimerSingleShot(False)
        else:
            self.pulseRepetitionButton.setText("Single Shot")
            self.worker.setTimerSingleShot(True)

    def valueChanged(self, spinBox, reference):
        if spinBox.value() != reference:
            spinBox.setStyleSheet("background-color: yellow;")
        else:
            spinBox.setStyleSheet("background-color: white;")
    
    def getPulseDuration(self):
        self.positionTriggerData.duration = self.editTriggerDuration.value()

    def getPositionTriggerData(self):
        self.positionTriggerData.start = self.editTriggerPosition.value()
        self.positionTriggerData.window = self.editTriggerWindow.value()
        self.positionTriggerData.retention = self.editTriggerRetention.value()
        self.getPulseDuration()

    def setButtonAction(self):
        self.getPositionTriggerData()
        self.valueChanged(self.editTriggerPosition, self.positionTriggerData.start)
        self.valueChanged(self.editTriggerWindow, self.positionTriggerData.window)
        self.valueChanged(self.editTriggerRetention, self.positionTriggerData.retention)

        self.positionTriggerChangedSignal.emit(self.positionTriggerData)

    def restoreButtonAction(self):
        self.editTriggerPosition.setValue(self.positionTriggerData.start)
        self.editTriggerWindow.setValue(self.positionTriggerData.window)
        self.editTriggerRetention.setValue(self.positionTriggerData.retention)

    def groupboxToggleAction(self, isToggled):
        self.positionTriggerData.isActive = isToggled
        if not isToggled:
            self.enableChildrenWidgets(self.groupboxPositionTrigger)
            self.worker.terminate()

    def enableChildrenWidgets(self, object):
        for child in object.findChildren(QWidget):
            child.setEnabled(True)
