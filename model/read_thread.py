import time
from PyQt5.QtCore import QObject, QThread, pyqtSignal, QTimer
from model.gtools import GTools
from interfaces.treadmill_data import TreadmillData

class Signals(QObject):
    message_sig = pyqtSignal(str)
    start_timer_sig = pyqtSignal()
    terminate_sig = pyqtSignal()
    finished = pyqtSignal()

class ReadThread(QThread):
    start_timer_sig = pyqtSignal()
    stop_timer_sig = pyqtSignal()
    terminate_sig = pyqtSignal()

    def __init__(self, treadmill, parent = None):
        super().__init__(parent=parent)
        self.worker = ReadThreadWorker(treadmill)
        self.worker.moveToThread(self)
        self.started.connect(self.worker.process)
        self.worker.finished.connect(self.quit)
        self.terminate_sig.connect(self.worker.terminate)
        
    def stop(self):
        self.terminate_sig.emit()

class ReadThreadWorker(QObject):
    message_sig = pyqtSignal(str)
    finished = pyqtSignal()
    samplingInterval = 5

    def __init__(self, treadmill):
        super().__init__()
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
        self.treadmill.data_read_signal.connect(self.update_self_treadmill_data)
        self.treadmill.data_read_signal.connect(self.record_treadmill_data)

    def process(self):
        self.running = True
        self.measurement_count = 0
        self.treadmill_data_list.clear()
        self.sampling_timer.start()
        self.message_sig.emit("Waiting for trigger...\n")

    def start_timer(self):
        self.sampling_timer.start()

    def stop_timer(self):
        self.sampling_timer.stop()

    def read_treadmill_data(self):
        self.treadmill.read_data()
        self.check_port_states()

    def update_self_treadmill_data(self, data):
        self.treadmill_data = data

    def record_treadmill_data(self, data):
        if self.recording:
            self.treadmill_data_list.append(data)

    def check_port_states(self):
        for port_list_instance, port_state in zip(self.port_list, self.treadmill_data.port_states):
            if not port_list_instance.port.writing:
                if not port_list_instance.port.groupbox_position_trigger.isChecked():
                    if port_list_instance.is_port_active != port_state:
                        print("\n\n\nMISSMATCH on port ", port_list_instance.port.name,
                            ", writing=", port_list_instance.port.writing,
                            port_list_instance.is_port_active, port_state, "\n\n\n")
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
        self.message_sig.emit('Recording #' + str(self.measurement_count) + ' started @' + start_date)
        self.file_name = self.save_folder + '/' + start_date + " (" + str(self.measurement_count).zfill(3) + ").csv"

    def finish_recording(self):
        self.recording = False
        self.message_sig.emit('Recording #' + str(self.measurement_count) + ' finished.\n')
        GTools.write_to_file(self.file_name, self.treadmill_data_list)
        self.treadmill_data_list.clear()
        self.message_sig.emit('Data written to: ' + self.file_name + '\n')
        self.message_sig.emit("Waiting for trigger...")

    def terminate(self):
        self.running = False
        self.sampling_timer.stop()
        self.finished.emit()