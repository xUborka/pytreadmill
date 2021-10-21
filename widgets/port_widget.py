from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtWidgets import QWidget, QPushButton, QLineEdit, QLabel,\
    QSpinBox, QGroupBox
from model.position_trigger import PositionTriggerWorker
from interfaces.port_data import PortData


class PortWidget(QWidget):
    position_trigger_changed_signal = pyqtSignal(object)

    def __init__(self, name, port_list, read_thread, treadmill):
        super().__init__()
        self.name = name
        self.treadmill = treadmill
        self.read_thread = read_thread
        self.port_data = PortData(self)

        self.writing = False
        self.writing_timer = QTimer(self)
        self.writing_timer.setInterval(500)
        self.writing_timer.setSingleShot(True)
        self.writing_timer.timeout.connect(self.writing_off)

        # create worker thread
        self.worker = PositionTriggerWorker(self.port_data)
        self.worker.triggerSignal.connect(self.pulse_signal_action)
        self.position_trigger_changed_signal.connect(self.worker.update_trigger_interval)

        # initialize UI elements
        self.label = QLabel(self.name)
        self.edit_label = QLineEdit()
        self.switch_button = QPushButton("OFF")
        self.edit_trigger_duration = QSpinBox()
        self.pulse_button = QPushButton("Impulse")
        self.pulse_repetition_button = QPushButton("Single Shot")
        self.edit_trigger_position = QSpinBox()
        self.edit_trigger_window = QSpinBox()
        self.edit_trigger_retention = QSpinBox()
        self.set_button = QPushButton("Set")
        self.restore_button = QPushButton("Restore")
        self.groupbox_position_trigger = QGroupBox()
        self.pulse_timer = QTimer()

        # set parameters of UI elements
        self.set_ui_elements()

        # update and send data about port instance to main thread
        self.get_port_data()
        self.init_spinbox()
        port_list.append(self.port_data)

    def set_ui_elements(self):
        self.edit_label.setPlaceholderText("port " + self.name)

        self.switch_button.setStyleSheet("color: white;" "background-color: red")
        self.switch_button.clicked.connect(self.port_switch_action)
        self.pulse_timer.timeout.connect(self.port_switch_action)

        self.edit_trigger_duration.setAlignment(Qt.AlignRight)
        self.edit_trigger_duration.setSuffix(" ms")
        self.edit_trigger_duration.valueChanged.connect(self.get_pulse_duration)

        self.pulse_button.clicked.connect(self.pulse_signal_action)

        self.pulse_repetition_button.setCheckable(True)
        self.pulse_repetition_button.setFocusPolicy(Qt.NoFocus)
        self.pulse_repetition_button.toggled.connect(self.pulse_repetition_button_action)

        self.edit_trigger_position.setAlignment(Qt.AlignRight)
        self.edit_trigger_position.setSuffix(" ‰")
        self.edit_trigger_position.valueChanged.connect(
            lambda: self.value_changed(self.edit_trigger_position, self.port_data.start))

        self.edit_trigger_window.setAlignment(Qt.AlignRight)
        self.edit_trigger_window.setSuffix(" ‰")
        self.edit_trigger_window.valueChanged.connect(
            lambda: self.value_changed(self.edit_trigger_window, self.port_data.window))

        self.edit_trigger_retention.setAlignment(Qt.AlignRight)
        self.edit_trigger_retention.setSuffix(" ms")
        self.edit_trigger_retention.valueChanged.connect(
            lambda: self.value_changed(self.edit_trigger_retention, self.port_data.retention))

        self.set_button.clicked.connect(self.set_button_action)
        self.restore_button.clicked.connect(self.restore_button_action)

        self.groupbox_position_trigger.setCheckable(True)
        self.groupbox_position_trigger.toggled.connect(self.groupbox_toggle_action)
        self.groupbox_position_trigger.setChecked(False)

    @staticmethod
    def init_single_spinbox(widget, minv, maxv, val, step):
        widget.setRange(minv, maxv)
        widget.setValue(val)
        widget.setSingleStep(step)

    def init_spinbox(self):
        PortWidget.init_single_spinbox(self.edit_trigger_duration, 100, 5000, 100, 100)
        PortWidget.init_single_spinbox(self.edit_trigger_position, 1, 1000, 500, 50)
        PortWidget.init_single_spinbox(self.edit_trigger_window, 0, 999, 100, 50)
        PortWidget.init_single_spinbox(self.edit_trigger_retention, 50, 10000, 3000, 500)
        self.set_button_action()

    def writing_off(self):
        self.writing = False

    def update_switch_button_visual(self):
        if self.port_data.is_port_active:
            self.switch_button.setText("ON")
            self.switch_button.setStyleSheet("color: white; background-color: green;")
            self.pulse_button.setDisabled(True)
        else:
            self.switch_button.setText("OFF")
            self.switch_button.setStyleSheet("color: white; background-color: red;")
            self.pulse_button.setDisabled(False)

    def port_switch_action(self):
        self.writing = True
        self.writing_timer.start()
        if self.port_data.is_port_active:
            self.pulse_timer.stop()
            self.treadmill.write_data(self.name.lower())
            self.port_data.is_port_active = False
            self.update_switch_button_visual()
        else:
            self.treadmill.write_data(self.name)
            self.port_data.is_port_active = True
            self.update_switch_button_visual()

    def pulse_signal_action(self):
        self.port_switch_action()
        self.pulse_timer.start(self.edit_trigger_duration.value())

    def pulse_repetition_button_action(self, checked):
        if checked:
            self.pulse_repetition_button.setText("Continuous Shot")
            self.worker.set_timer_single_shot(False)
        else:
            self.pulse_repetition_button.setText("Single Shot")
            self.worker.set_timer_single_shot(True)

    def value_changed(self, spin_box, reference):
        if spin_box.value() != reference:
            spin_box.setStyleSheet("background-color: yellow;")
        else:
            spin_box.setStyleSheet("background-color: white;")

    def get_pulse_duration(self):
        self.port_data.duration = self.edit_trigger_duration.value()

    def get_port_data(self):
        self.port_data.start = self.edit_trigger_position.value()
        self.port_data.window = self.edit_trigger_window.value()
        self.port_data.retention = self.edit_trigger_retention.value()
        self.get_pulse_duration()

    def set_button_action(self):
        self.get_port_data()
        self.value_changed(self.edit_trigger_position, self.port_data.start)
        self.value_changed(self.edit_trigger_window, self.port_data.window)
        self.value_changed(self.edit_trigger_retention, self.port_data.retention)

        self.position_trigger_changed_signal.emit(self.port_data)

    def restore_button_action(self):
        self.edit_trigger_position.setValue(self.port_data.start)
        self.edit_trigger_window.setValue(self.port_data.window)
        self.edit_trigger_retention.setValue(self.port_data.retention)

    def groupbox_toggle_action(self, is_toggled):
        self.port_data.is_trigger_active = is_toggled
        if is_toggled:
            self.enable_children_widgets(self.groupbox_position_trigger)
            self.worker.process()
        else:
            self.worker.terminate()

    def enable_children_widgets(self, obj):
        for child in obj.findChildren(QWidget):
            child.setEnabled(True)
