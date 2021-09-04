from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QGroupBox
from widgets.port_widget import PortWidget


class PortGroupWidget(QGroupBox):
    def __init__(self, port_list, read_thread, treadmill):
        super().__init__("Port Settings")
        self.port_a = PortWidget("A", port_list, read_thread, treadmill)
        layout_port_a = PortGroupWidget.init_port_ui(self.port_a)

        # Port B Widgets
        self.port_b = PortWidget("B", port_list, read_thread, treadmill)
        layout_port_b = PortGroupWidget.init_port_ui(self.port_b)

        # Port C Widgets
        self.port_c = PortWidget("C", port_list, read_thread, treadmill)
        layout_port_c = PortGroupWidget.init_port_ui(self.port_c)

        # Layout for All Port Layouts
        layout_all_ports = QVBoxLayout()
        layout_all_ports.addLayout(layout_port_a)
        layout_all_ports.addLayout(layout_port_b)
        layout_all_ports.addLayout(layout_port_c)

        self.setEnabled(False)
        self.setLayout(layout_all_ports)

    @staticmethod
    def init_port_ui(port_widget):
        layout_port = QHBoxLayout()
        layout_port.addWidget(port_widget.label)
        layout_port.addWidget(port_widget.edit_label)
        layout_port.addWidget(port_widget.switch_button)
        layout_port.addWidget(port_widget.edit_trigger_duration)
        layout_port.addWidget(port_widget.pulse_button)

        layout_port_position_trigger = QHBoxLayout()
        layout_port_position_trigger.addWidget(port_widget.pulse_repetition_button)
        layout_port_position_trigger.addWidget(port_widget.edit_trigger_position)
        layout_port_position_trigger.addWidget(port_widget.edit_trigger_window)
        layout_port_position_trigger.addWidget(port_widget.edit_trigger_retention)
        layout_port_position_trigger.addWidget(port_widget.set_button)
        layout_port_position_trigger.addWidget(port_widget.restore_button)
        port_widget.groupbox_position_trigger.setLayout(layout_port_position_trigger)
        port_widget.groupbox_position_trigger.setChecked(False)

        layout_port.addWidget(port_widget.groupbox_position_trigger)

        return layout_port
