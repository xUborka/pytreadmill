from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtWidgets import QWidget, QPushButton, QLineEdit, QLabel,\
    QSpinBox, QGroupBox
from model.position_trigger import PositionTriggerWorker
from interfaces.position_trigger_data import PositionTriggerData


class PortWidget(QWidget):
    position_trigger_changed_signal = pyqtSignal(object)

    def __init__(self, name, port_list, read_thread, treadmill):
        super().__init__()
        self.name = name
        self.treadmill = treadmill
        self.read_thread = read_thread
        self.position_trigger_data = PositionTriggerData(self)

        self.clicked = True

        # create worker thread
        self.worker = PositionTriggerWorker(self.position_trigger_data)
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
        self.get_position_trigger_data()
        self.init_spinbox()
        port_list.append(self.position_trigger_data)

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
            lambda: self.value_changed(self.edit_trigger_position, self.position_trigger_data.start))

        self.edit_trigger_window.setAlignment(Qt.AlignRight)
        self.edit_trigger_window.setSuffix(" ‰")
        self.edit_trigger_window.valueChanged.connect(
            lambda: self.value_changed(self.edit_trigger_window, self.position_trigger_data.window))

        self.edit_trigger_retention.setAlignment(Qt.AlignRight)
        self.edit_trigger_retention.setSuffix(" ms")
        self.edit_trigger_retention.valueChanged.connect(
            lambda: self.value_changed(self.edit_trigger_retention, self.position_trigger_data.retention))

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

    def port_switch_action(self):
        if self.clicked:
            self.switch_button.setText("ON")
            self.switch_button.setStyleSheet("color: white; background-color: green;")
            self.pulse_button.setDisabled(True)
            self.treadmill.write_data(self.name)
            self.clicked = False
        else:
            self.switch_button.setText("OFF")
            self.switch_button.setStyleSheet("color: white; background-color: red;")
            self.pulse_button.setDisabled(False)
            self.pulse_timer.stop()
            self.treadmill.write_data(self.name.lower())
            self.clicked = True

    def pulse_signal_action(self):
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
        self.position_trigger_data.duration = self.edit_trigger_duration.value()

    def get_position_trigger_data(self):
        self.position_trigger_data.start = self.edit_trigger_position.value()
        self.position_trigger_data.window = self.edit_trigger_window.value()
        self.position_trigger_data.retention = self.edit_trigger_retention.value()
        self.get_pulse_duration()

    def set_button_action(self):
        self.get_position_trigger_data()
        self.value_changed(self.edit_trigger_position, self.position_trigger_data.start)
        self.value_changed(self.edit_trigger_window, self.position_trigger_data.window)
        self.value_changed(self.edit_trigger_retention, self.position_trigger_data.retention)

        self.position_trigger_changed_signal.emit(self.position_trigger_data)

    def restore_button_action(self):
        self.edit_trigger_position.setValue(self.position_trigger_data.start)
        self.edit_trigger_window.setValue(self.position_trigger_data.window)
        self.edit_trigger_retention.setValue(self.position_trigger_data.retention)

    def groupbox_toggle_action(self, is_toggled):
        self.position_trigger_data.is_active = is_toggled
        if is_toggled:
            self.enable_children_widgets(self.groupbox_position_trigger)
            self.worker.process()
        else:
            self.worker.terminate()

    def enable_children_widgets(self, obj):
        for child in obj.findChildren(QWidget):
            child.setEnabled(True)
