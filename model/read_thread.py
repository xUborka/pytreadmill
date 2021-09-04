import time
from PyQt5.QtCore import QThread, pyqtSignal
from model.gtools import GTools
from interfaces.treadmill_data import TreadmillData


class ReadThread(QThread):
    print_data_signal = pyqtSignal(str)
    message_signal = pyqtSignal(str)
    treadmill_state_changed = pyqtSignal(str)

    def __init__(self, treadmill, parent=None):
        super().__init__(parent)
        self.treadmill = treadmill
        self.initialized = False
        self.running = False
        self.record = False
        self.save_folder = None
        self.measurement_count = 0
        self.port_list = list()
        self.treadmill_data = TreadmillData()

        self.treadmill_data_list = list()

    def print_data_to_gui(self, prefix):
        self.print_data_signal.emit(prefix +
                                  "   |   v = " + str(self.treadmill_data.velocity) +
                                  "   |   abs. position = " + str(self.treadmill_data.abs_position) +
                                  "   |   lap = " + str(self.treadmill_data.lap) +
                                  "   |   rel. position = " + str(self.treadmill_data.rel_position) + "    ")

    def check_port_states(self):
        for port_list_instance, port_state in zip(self.port_list, self.treadmill_data.port_states):
            if not port_list_instance.port.groupbox_position_trigger.isChecked():
                if port_list_instance.is_active != port_state:
                    port_list_instance.port.switch_button.setChecked(bool(port_state))

    def finish_recording(self, filename):
        self.record = False
        self.message_signal.emit('Recording #' + str(self.measurement_count) + ' finished.\n')
        GTools.write_to_file(filename, self.treadmill_data_list)
        self.treadmill_data_list.clear()
        self.message_signal.emit('Data written to: ' + filename + '\n')
        self.message_signal.emit("Waiting for trigger...")

    def send_init_signal(self):
        if self.initialized:
            self.treadmill_state_changed.emit("initialized")
        else:
            self.treadmill_state_changed.emit("uninitialized")

    def run(self):
        self.record = False
        self.measurement_count = 0

        self.treadmill_data_list.clear()
        self.message_signal.emit("Waiting for trigger...")

        while self.running and self.treadmill.connected:
            self.treadmill_data = self.treadmill.read_data()
            self.print_data_to_gui("")
            self.check_port_states()
            if self.initialized != self.treadmill_data.initialized:
                self.initialized = bool(self.treadmill_data.initialized)
                self.send_init_signal()

            if self.treadmill_data.recording == 1:
                self.record = True
                self.measurement_count += 1
                self.treadmill_state_changed.emit("recording")

                start_date = time.strftime("%Y-%m-%d %H_%M_%S")
                self.message_signal.emit('Recording #' + str(self.measurement_count) + ' started @' + start_date)
                filename = self.save_folder + '/' + start_date + " (" + str(self.measurement_count).zfill(3) + ").csv"

            while self.running and self.record:
                self.print_data_to_gui(str("Recording... " +
                                       time.strftime("%M:%S", time.gmtime(int(self.treadmill_data.time) / 1000))))
                self.treadmill_data_list.append(self.treadmill_data)
                self.treadmill_data = self.treadmill.read_data()

                if self.treadmill_data.recording == 0:
                    self.finish_recording(filename)
                    self.send_init_signal()
