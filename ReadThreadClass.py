from PyQt5.QtCore import QThread, pyqtSignal
import time
from gtools import GTools
from treadmill_data import TreadmillData


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
        self.measurementCount = int()
        self.portList = list()
        self.positionTriggerThreads = list()
        self.treadmillData = TreadmillData()

        self.treadmill_data_list = list()

    def getTreadmillData(self):
        return self.treadmillData

    def emptyLists(self):
        self.treadmill_data_list.clear()

    def appendData2Lists(self):
        self.treadmill_data_list.append(self.treadmillData)

    def printData2GUI(self, prefix):
        self.printDataSignal.emit(prefix +
                                  "   |   v = " + str(self.treadmillData.velocity) +
                                  "   |   abs. position = " + str(self.treadmillData.absPosition) +
                                  "   |   lap = " + str(self.treadmillData.lap) +
                                  "   |   rel. position = " + str(self.treadmillData.relPosition) + "    ")

    def checkPositionTriggerEvent(self):
        position = self.treadmillData.relPosition
        for portListInstance in self.portList:
            try:
                if portListInstance.isActive:
                    if not portListInstance.thread.isRunning():
                        if portListInstance.start <= position <= (portListInstance.start + portListInstance.window):
                            portListInstance.thread.start()
            except Exception as e:
                print(e)

    def checkPortStates(self):
        for portListInstance, portState in zip(self.portList, self.treadmillData.portStates):
            if not portListInstance.port.groupboxPositionTrigger.isChecked():
                if portListInstance.isActive != portState:
                    portListInstance.port.switchButton.setChecked(bool(portState))

    def finishRecording(self, filename):
        self.record = False
        self.messageSignal.emit('Recording #' + str(self.measurementCount) + ' finished.\n')
        GTools.write2File(filename, self.treadmill_data_list)
        self.emptyLists()
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

        self.emptyLists()
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
                self.appendData2Lists()
                self.treadmillData = self.treadmill.readData()
                self.checkPositionTriggerEvent()

                if self.treadmillData.recording == 0:
                    self.finishRecording(filename)
                    self.sendInitializationSignal()

        if self.running and not self.treadmill.connected:
            pass  # treadmill unplugged
