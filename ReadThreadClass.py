import time
from PyQt5.QtCore import QThread, pyqtSignal
from gtools import GTools
from interfaces.treadmill_data import TreadmillData


class ReadThreadClass(QThread):
    printDataSignal = pyqtSignal(str)
    messageSignal = pyqtSignal(str)
    treadmillStateChanged = pyqtSignal(str)

    def __init__(self, treadmill, parent=None):
        super(ReadThreadClass, self).__init__(parent)
        self.treadmill = treadmill
        self.initialized = False
        self.running = False
        self.record = False
        self.saveFolder = None
        self.measurementCount = 0
        self.portList = list()
        self.treadmillData = TreadmillData()

        self.treadmill_data_list = list()

    def printData2GUI(self, prefix):
        self.printDataSignal.emit(prefix +
                                  "   |   v = " + str(self.treadmillData.velocity) +
                                  "   |   abs. position = " + str(self.treadmillData.absPosition) +
                                  "   |   lap = " + str(self.treadmillData.lap) +
                                  "   |   rel. position = " + str(self.treadmillData.relPosition) + "    ")

    def checkPortStates(self):
        for portListInstance, portState in zip(self.portList, self.treadmillData.portStates):
            if not portListInstance.port.groupboxPositionTrigger.isChecked():
                if portListInstance.is_active != portState:
                    portListInstance.port.switchButton.setChecked(bool(portState))

    def finishRecording(self, filename):
        self.record = False
        self.messageSignal.emit('Recording #' + str(self.measurementCount) + ' finished.\n')
        GTools.write2File(filename, self.treadmill_data_list)
        self.treadmill_data_list.clear()
        self.messageSignal.emit('Data written to: ' + filename + '\n')
        self.messageSignal.emit("Waiting for trigger...")

    def sendInitializationSignal(self):
        if self.initialized:
            self.treadmillStateChanged.emit("initialized")
        else:
            self.treadmillStateChanged.emit("uninitialized")

    def run(self):
        self.record = False
        self.measurementCount = 0

        self.treadmill_data_list.clear()
        self.messageSignal.emit("Waiting for trigger...")

        while self.running and self.treadmill.connected:
            self.treadmillData = self.treadmill.readData()
            self.printData2GUI("")
            self.checkPortStates()
            if self.initialized != self.treadmillData.initialized:
                self.initialized = bool(self.treadmillData.initialized)
                self.sendInitializationSignal()

            if self.treadmillData.recording == 1:
                self.record = True
                self.measurementCount += 1
                self.treadmillStateChanged.emit("recording")

                startDate = time.strftime("%Y-%m-%d %H_%M_%S")
                self.messageSignal.emit('Recording #' + str(self.measurementCount) + ' started @' + startDate)
                filename = self.saveFolder + '/' + startDate + " (" + str(self.measurementCount).zfill(3) + ").csv"

            while self.running and self.record:
                self.printData2GUI(str("Recording... " +
                                       time.strftime("%M:%S", time.gmtime(int(self.treadmillData.time) / 1000))))
                self.treadmill_data_list.append(self.treadmillData)
                self.treadmillData = self.treadmill.readData()

                if self.treadmillData.recording == 0:
                    self.finishRecording(filename)
                    self.sendInitializationSignal()
