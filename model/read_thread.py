import time
from PyQt5.QtCore import QObject, QThread, pyqtSignal, QTimer
from model.gtools import GTools
from interfaces.treadmill_data import TreadmillData


class ReadThreadWorker(QObject):
    message_signal = pyqtSignal(str)
    start_timer_sig = pyqtSignal()
    terminate_sig = pyqtSignal()
    finished = pyqtSignal()
    samplingInterval = 5

    def __init__(self, treadmill, parent=None):
        super().__init__(parent)
        self.treadmill = treadmill
        self.initialized = False
        self.running = False
        self.recording = False
        self.file_name = None
        self.save_folder = None
        self.measurement_count = 0
        self.port_list = list()
        self.treadmill_data = TreadmillData()
        self.treadmill_data_list = list()

        self.sampling_timer = QTimer(self)
        self.sampling_timer.setInterval(self.samplingInterval)
        self.sampling_timer.timeout.connect(self.read_treadmill_data)

        self.treadmill.record_signal.connect(self.recording_switch)
        self.terminate_sig.connect(self.terminate)

    def process(self):
        self.running = True
        self.measurement_count = 0
        self.treadmill_data_list.clear()
        self.start_timer_sig.emit()
        self.message_signal.emit("Waiting for trigger...")

    def start_timer(self):
        self.sampling_timer.start()

    def read_treadmill_data(self):
        self.treadmill_data = self.treadmill.read_data()
        self.check_port_states()
        if self.recording:
            self.treadmill_data_list.append(self.treadmill_data)

    def check_port_states(self):
        # print(self.port_list[0].is_port_active, self.treadmill_data.port_states[0])
        for port_list_instance, port_state in zip(self.port_list, self.treadmill_data.port_states):
            if not port_list_instance.port.groupbox_position_trigger.isChecked():
                if port_list_instance.is_port_active != port_state:
                    """ print("\n\n\nMISSMATCH on port ", port_list_instance.port.name,
                        ", writing=", port_list_instance.port.writing,
                        port_list_instance.is_port_active, port_state, "\n\n\n") """
                    port_list_instance.is_port_active = bool(port_state)
                    port_list_instance.port.update_switch_button_visual()

    def recording_switch(self, is_recording):
        if is_recording:
            self.init_recording()
        else:
            self.finish_recording()

    def init_recording(self):
        self.recording = True
        self.measurement_count += 1
        start_date = time.strftime("%Y-%m-%d %H_%M_%S")
        self.message_signal.emit('Recording #' + str(self.measurement_count) + ' started @' + start_date)
        self.file_name = self.save_folder + '/' + start_date + " (" + str(self.measurement_count).zfill(3) + ").csv"

    def finish_recording(self):
        self.recording = False
        self.message_signal.emit('Recording #' + str(self.measurement_count) + ' finished.\n')
        GTools.write_to_file(self.file_name, self.treadmill_data_list)
        self.treadmill_data_list.clear()
        self.message_signal.emit('Data written to: ' + self.file_name + '\n')
        self.message_signal.emit("Waiting for trigger...")

    def terminate(self):
        self.running = False
        self.sampling_timer.stop()
        self.finished.emit()