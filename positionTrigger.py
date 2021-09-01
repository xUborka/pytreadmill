from PyQt5.QtCore import pyqtSignal, QTimer, QObject


class PositionTriggerData:
    def __init__(self, port=None):
        self.port = port
        self.is_active = False

        self.start = 0
        self.window = 0
        self.retention = 0
        self.duration = 0


class PositionTriggerWorker(QObject):
    triggerSignal = pyqtSignal()
    finishedSignal = pyqtSignal()
    checkerInterval = 50

    def __init__(self, parent_trigger_data, parent=None):
        super(PositionTriggerWorker, self).__init__(parent)
        self.positionTriggerData = parent_trigger_data

        self.isRunning = True
        self.isSingleShot = True
        self.hasFired = False

        self.triggerTimer = QTimer(self)
        self.triggerTimer.setSingleShot(False)
        self.triggerTimer.timeout.connect(self.trigger)

        self.checkerTimer = QTimer(self)
        self.checkerTimer.setSingleShot(False)
        self.checkerTimer.timeout.connect(self.checkPosition)

    def process(self):
        self.hasFired = False
        self.checkerTimer.start(self.checkerInterval)


    def trigger(self):
        if self.isSingleShot:
            if not self.hasFired:
                self.triggerSignal.emit()
        else:
            self.triggerSignal.emit()
        self.hasFired = True

    def setTimerSingleShot(self, isSingleShot):
        self.isSingleShot = isSingleShot

    def updateTriggerInterval(self):
        self.triggerTimer.setInterval(self.positionTriggerData.retention)

    def checkPosition(self):
        treadmill_data = self.positionTriggerData.port.treadmill_data.treadmillData
        if self.positionTriggerData.start < treadmill_data.relPosition < self.positionTriggerData.start + self.positionTriggerData.window:
            if not self.triggerTimer.isActive():
                self.triggerTimer.start(self.positionTriggerData.retention)
        else:
            self.hasFired = False
            self.triggerTimer.stop()

    def terminate(self):
        self.isRunning = False
        self.hasFired = False
        self.checkerTimer.stop()
        self.triggerTimer.stop()
