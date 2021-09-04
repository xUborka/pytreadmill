from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtWidgets import QWidget, QPushButton, QLineEdit, QLabel,\
    QSpinBox, QGroupBox
from positionTrigger import PositionTriggerWorker
from interfaces.position_trigger_data import PositionTriggerData


class Port(QWidget):
    positionTriggerChangedSignal = pyqtSignal(object)

    def __init__(self, name, port_list, treadmill_data, treadmill):
        super(Port, self).__init__()
        self.name = name
        self.treadmill = treadmill
        self.treadmill_data = treadmill_data
        self.positionTriggerData = PositionTriggerData(self)

        self.clicked = True

        # create worker thread
        self.worker = PositionTriggerWorker(self.positionTriggerData)
        self.worker.triggerSignal.connect(self.pulseSignalAction)
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
        self.init_spinbox()
        port_list.append(self.positionTriggerData)

    def setUIElements(self):
        self.editLabel.setPlaceholderText("port " + self.name)

        self.switchButton.setStyleSheet("color: white;" "background-color: red")
        self.switchButton.clicked.connect(self.portSwitchAction)
        self.pulseTimer.timeout.connect(self.portSwitchAction)

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

    @staticmethod
    def init_single_spinbox(widget, minv, maxv, val, step):
        widget.setRange(minv, maxv)
        widget.setValue(val)
        widget.setSingleStep(step)

    def init_spinbox(self):
        Port.init_single_spinbox(self.editTriggerDuration, 100, 5000, 100, 100)
        Port.init_single_spinbox(self.editTriggerPosition, 1, 1000, 500, 50)
        Port.init_single_spinbox(self.editTriggerWindow, 0, 999, 100, 50)
        Port.init_single_spinbox(self.editTriggerRetention, 50, 10000, 3000, 500)
        self.setButtonAction()

    def portSwitchAction(self):
        if self.clicked:
            self.switchButton.setText("ON")
            self.switchButton.setStyleSheet("color: white; background-color: green;")
            self.pulseButton.setDisabled(True)
            self.treadmill.writeData(self.name)
            self.clicked = False
        else:
            self.switchButton.setText("OFF")
            self.switchButton.setStyleSheet("color: white; background-color: red;")
            self.pulseButton.setDisabled(False)
            self.pulseTimer.stop()
            self.treadmill.writeData(self.name.lower())
            self.clicked = True

    def pulseSignalAction(self):
        print("PULSE")
        self.pulseTimer.start(self.editTriggerDuration.value())

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
        self.positionTriggerData.is_active = isToggled
        if isToggled:
            self.enableChildrenWidgets(self.groupboxPositionTrigger)
            self.worker.process()
        else:
            self.worker.terminate()

    def enableChildrenWidgets(self, obj):
        for child in obj.findChildren(QWidget):
            child.setEnabled(True)
