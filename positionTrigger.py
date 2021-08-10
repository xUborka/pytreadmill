from PyQt5.QtCore import QThread, pyqtSignal, QTimer, QObject


class PositionTriggerData:
    def __init__(self, port=None):
        self.port = port
        self.thread: QThread = None
        self.isActive = False

        self.start = 0
        self.window = 0
        self.retention = 0
        self.duration = 0


class PositionTriggerWorker(QObject):
    triggerSignal = pyqtSignal()
    finished = pyqtSignal()
    checkerInterval = 50

    def __init__(self, positionTriggerData, parent=None):
        super(PositionTriggerWorker, self).__init__(parent)

        self.positionTriggerData = positionTriggerData

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
        self.triggerTimer.start(self.positionTriggerData.retention)

    def trigger(self):
        if self.isSingleShot:
            if not self.hasFired:
                self.triggerSignal.emit()
                # print("triggerTimer fired")
        else:
            self.triggerSignal.emit()
            # print("triggerTimer fired")
        self.hasFired = True

    def setTimerSingleShot(self, isSingleShot):
        # self.triggerTimer.setInterval(self.positionTriggerData.retention)
        self.isSingleShot = isSingleShot

    def updateTriggerInterval(self):
        self.triggerTimer.setInterval(self.positionTriggerData.retention)

    def checkPosition(self):
        treadmillData = self.positionTriggerData.port.getTreadmillData()
        if treadmillData.relPosition < self.positionTriggerData.start \
                or treadmillData.relPosition > (self.positionTriggerData.start + self.positionTriggerData.window):
            self.terminate()

    def terminate(self):
        self.isRunning = False
        self.hasFired = False
        self.checkerTimer.stop()
        self.triggerTimer.stop()
        self.finished.emit()
