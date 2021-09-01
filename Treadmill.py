import serial
import serial.tools.list_ports
from PyQt5.QtCore import QObject, pyqtSignal
from gtools import GTools
from treadmill_data import TreadmillData


class Treadmill(QObject):
    connectionSignal = pyqtSignal(bool)
    initializationSignal = pyqtSignal(bool)
    recordSignal = pyqtSignal(bool)

    def __init__(self):
        super(Treadmill, self).__init__()

        self.connected = False
        self.initialized = False
        self.recording = False

        self.treadmillData = TreadmillData()

        self.serialObject = None

        self.connectionSignal.connect(self.setConnectionState)
        self.initializationSignal.connect(self.setInitializationState)
        self.recordSignal.connect(self.setRecordingState)

    @staticmethod
    def findTreadmills():
        print([p.device for p in serial.tools.list_ports.comports()])
        arduinoPorts = [
            p.device
            for p in serial.tools.list_ports.comports()
            if p.serial_number == "A600HISAA" or p.pid == 32847 or p.pid == 67]
        return arduinoPorts

    def connect(self, port):
        print('Connecting to Treadmill on port ' + port + '\n')
        self.serialObject = None

        try:  # ...to connect to treadmill
            self.serialObject = serial.Serial(port, 115200)
        except serial.SerialException as exc:
            print(exc)
            self.connectionSignal.emit(False)
            return False
        else:
            print("Serial connection established.\n")
            self.connectionSignal.emit(True)
            return True

    def closeConnection(self):
        self.serialObject.close()
        self.connectionSignal.emit(False)
        print("Serial connection terminated.")

    def setConnectionState(self, state: bool):
        self.connected = state

    def setInitializationState(self, state: bool):
        self.initialized = state

    def setRecordingState(self, state: bool):
        self.recording = state

    def updateTreadmillState(self):
        if self.treadmillData.initialized != self.initialized:
            if 1 == self.treadmillData.initialized:
                self.initializationSignal.emit(True)
            else:
                self.initializationSignal.emit(False)

        if self.treadmillData.recording != self.recording:
            if 1 == self.treadmillData.recording:
                self.recordSignal.emit(True)
            else:
                self.recordSignal.emit(False)

    def readData(self):
        try:
            serialInput = self.serialObject.readline()
            serialInput = serialInput.decode(encoding='ascii')
            serialInput = serialInput.rstrip()
            self.treadmillData = TreadmillData(*serialInput.split(" "))
        except serial.SerialException as exc:
            GTools.error_message("Treadmill unplugged", exc)
            self.connectionSignal.emit(False)
            self.treadmillData.invalidate()
        except (ValueError, UnicodeDecodeError) as exc:
            GTools.error_message("Serial communication error", exc)
            self.treadmillData.invalidate()
        except Exception as exc:
            GTools.error_message("Unknown error during reading serial data", exc)
            self.treadmillData.invalidate()
        self.updateTreadmillState()
        return self.treadmillData

    def writeData(self, data):
        self.serialObject.write(bytes(data, 'ascii'))
