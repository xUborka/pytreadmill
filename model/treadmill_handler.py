import serial
import serial.tools.list_ports
from time import time_ns
from numpy import zeros, average
from PyQt5.QtCore import QObject, pyqtSignal
from model.gtools import GTools
from interfaces.treadmill_data import TreadmillData


class Treadmill(QObject):
    connection_signal = pyqtSignal(bool)
    init_signal = pyqtSignal(bool)
    record_signal = pyqtSignal(bool)
    ls_alarm_signal = pyqtSignal(bool)
    data_read_signal = pyqtSignal(TreadmillData)

    def __init__(self):
        super().__init__()

        self.current_time = time_ns() * 1000
        self.prev_time = self.current_time
        self.cycle_time_list = zeros(100)
        self.diff_time = 0

        self.connected = False
        self.initialized = False
        self.recording = False
        self.lap_sensor_alarm = False

        self.treadmill_data = TreadmillData()

        self.serial_object = None

        self.connection_signal.connect(self.set_connection_state)
        self.init_signal.connect(self.set_initialization_state)
        self.record_signal.connect(self.set_recording_state)
        self.ls_alarm_signal.connect(self.set_ls_alarm_state)

    @staticmethod
    def find_treadmills():
        ardunio_ports = [
            p.device
            for p in serial.tools.list_ports.comports()
            if p.serial_number == "A600HISAA" or p.pid == 32847 or p.pid == 67]
        return ardunio_ports

    def connect(self, port):
        print('Connecting to Treadmill on port ' + port + '\n')
        self.serial_object = None

        try:  # ...to connect to treadmill
            self.serial_object = serial.Serial(port, 115200)
        except serial.SerialException as exc:
            print(exc)
            self.connection_signal.emit(False)
            return False
        else:
            print("Serial connection established.\n")
            self.connection_signal.emit(True)
            return True

    def close_connection(self):
        self.serial_object.close()
        self.connection_signal.emit(False)
        print("Serial connection terminated.")

    def set_connection_state(self, state: bool):
        self.connected = state

    def set_initialization_state(self, state: bool):
        self.initialized = state

    def set_recording_state(self, state: bool):
        self.recording = state

    def set_ls_alarm_state(self, state: bool):
        self.lap_sensor_alarm = state

    def update_treadmill_state(self):
        if self.treadmill_data.initialized != self.initialized:
            self.init_signal.emit(bool(self.treadmill_data.initialized))

        if self.treadmill_data.recording != self.recording:
            if self.treadmill_data.recording == 1:
                self.record_signal.emit(True)
            elif self.treadmill_data.recording == 0:
                self.record_signal.emit(False)

        if self.treadmill_data.lap_sensor_alarm != self.lap_sensor_alarm:
            self.ls_alarm_signal.emit(bool(self.treadmill_data.lap_sensor_alarm))

    def allocate_serial_data(self):
        raw_serial_input = self.serial_object.read_until(b'>')
        # self.serial_object.reset_input_buffer()
        serial_input = raw_serial_input.decode(encoding='ascii')
        serial_input = serial_input[:-1]
        serial_input = serial_input.rstrip()
        self.treadmill_data = TreadmillData(*serial_input.split(" "))

    def read_data(self):
        while self.serial_object.isOpen() and self.serial_object.in_waiting > 2:
            try:
                self.allocate_serial_data()
            except serial.SerialException as exc:
                GTools.error_message("Treadmill unplugged", exc)
                self.connection_signal.emit(False)
                self.treadmill_data.invalidate()
            except (ValueError, UnicodeDecodeError) as exc:
                GTools.error_message("Serial communication error", exc)
                self.treadmill_data.invalidate()
            except Exception as exc:
                GTools.error_message("Unknown error during reading serial data", exc)
                self.treadmill_data.invalidate()

            self.update_treadmill_state()
            self.data_read_signal.emit(self.treadmill_data)

            self.update_cycle_time()

    def write_data(self, data):
        self.serial_object.write(bytes(data, 'ascii'))

    def update_cycle_time(self):
        self.prev_time = self.current_time
        self.current_time = time_ns() / 1000
        self.cycle_time_list[:-1] = self.cycle_time_list[1:]
        self.cycle_time_list[-1] = self.current_time - self.prev_time

        self.diff_time = average(self.cycle_time_list)
