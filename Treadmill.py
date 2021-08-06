import serial
import serial.tools.list_ports
import gtools
from dataclasses import dataclass
from PyQt5.QtCore import QObject, pyqtSignal


@dataclass
class TreadmillData:
    time: int = None
    recording: int = None
    velocity: int = None
    absPosition: int = None
    lap: int = None
    relPosition: int = None
    lick: int = None
    initialized: int = None
    portStates: tuple = None


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

        self.connectionSignal.connect(self.setConnectionState)
        self.initializationSignal.connect(self.setInitializationState)
        self.recordSignal.connect(self.setRecordingState)

    @staticmethod
    def findTreadmills():
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
    # 		if self.logFilename is not None: gtools.log_error(self.logFilename, "No Treadmill found")
    # 		print("Retry in 5 seconds...\n")
    # 		sleep(5)
    # 		arduinoPorts = self.findTreadmills()
    # 	if len(arduinoPorts) > 1: print("Warning: Multiple Treadmills found - using the first")
    # 	self.connect(arduinoPorts[0])

    def setConnectionState(self, boolean):
        self.connected = boolean

    def setInitializationState(self, boolean):
        self.initialized = boolean

    def setRecordingState(self, boolean):
        self.recording = boolean

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

    def allocateSerialData(self, serialInput):
        time, recording, velocity, absPosition, lap, relPosition, lick, initialized, portStates = serialInput.split(" ")

        self.treadmillData.time = int(time)
        self.treadmillData.recording = int(recording)
        self.treadmillData.velocity = int(velocity)
        self.treadmillData.absPosition = int(absPosition)
        self.treadmillData.lap = int(lap)
        self.treadmillData.relPosition = int(relPosition)
        self.treadmillData.lick = int(lick)
        self.treadmillData.initialized = int(initialized)
        self.treadmillData.portStates = list(map(int, portStates))

    def errorTreadmillData(self):
        self.treadmillData.time = 0
        self.treadmillData.recording = -1
        self.treadmillData.velocity = 0
        self.treadmillData.absPosition = 0
        self.treadmillData.lap = 0
        self.treadmillData.relPosition = 0
        self.treadmillData.lick = 0
        self.treadmillData.initialized = 0
        self.treadmillData.portStates = [0, 0, 0]

    def readData(self):
        try:
            serialInput = self.serialObject.readline()
            serialInput = serialInput.decode(encoding='ascii')
            serialInput = serialInput.rstrip()
            self.allocateSerialData(serialInput)

        except serial.SerialException as e:
            print(e)
            print("Treadmill uplugged")
            if self.logFilename is not None:
                gtools.log_error(self.logFilename, str(e) + " Treadmill unplugged")

            self.connectionSignal.emit(False)
            self.errorTreadmillData()
            self.updateTreadmillState()
            return self.treadmillData

        except (ValueError, UnicodeDecodeError) as e:
            print(e)
            print("Serial communication error")
            if self.logFilename is not None:
                gtools.log_error(self.logFilename, str(e) + " Serial communication error")

            self.errorTreadmillData()
            self.updateTreadmillState()
            return self.treadmillData

        except:
            print("Unknown error during reading serial data.")
            self.errorTreadmillData()
            self.updateTreadmillState()
            return self.treadmillData

        else:
            self.updateTreadmillState()
            return self.treadmillData

    def writeData(self, data):
        self.serialObject.write(bytes(data, 'ascii'))
