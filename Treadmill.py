import serial
import serial.tools.list_ports
from gtools import GTools
from PyQt5.QtCore import QObject, pyqtSignal
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
        self.logFilename = None

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
        except serial.SerialException as e:
            print(e)
            print(
                "Error: Serial connection cannot be established. Device in use by an other process or cannot be found.")
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

    # def autoConnect(self):
    # 	arduinoPorts = self.findTreadmills()
    # 	while not arduinoPorts:
    # 		print("Error: No Treadmill found. Please connect one.")
    # 		if self.logFilename is not None: GTools.log_error(self.logFilename, "No Treadmill found")
    # 		print("Retry in 5 seconds...\n")
    # 		sleep(5)
    # 		arduinoPorts = self.findTreadmills()
    # 	if len(arduinoPorts) > 1: print("Warning: Multiple Treadmills found - using the first")
    # 	self.connect(arduinoPorts[0])

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
        except serial.SerialException as e:
            GTools.error_message("Treadmill unplugged", e)
            self.connectionSignal.emit(False)
            self.treadmillData.invalidate()
        except (ValueError, UnicodeDecodeError) as e:
            GTools.error_message("Serial communication error", e)
            self.treadmillData.invalidate()
        except Exception as e:
            GTools.error_message("Unknown error during reading serial data", e)
            self.treadmillData.invalidate()
        self.updateTreadmillState()
        return self.treadmillData

    def writeData(self, data):
        self.serialObject.write(bytes(data, 'ascii'))
