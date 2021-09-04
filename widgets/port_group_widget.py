from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QGroupBox
from widgets.port_widget import PortWidget


class PortGroupWidget(QGroupBox):
    def __init__(self, port_list, get_treadmill_data, treadmill):
        super().__init__("Port Settings")
        self.port_a = PortWidget("A", port_list, get_treadmill_data, treadmill)
        layout_port_a = PortGroupWidget.init_port_ui(self.port_a)

        # Port B Widgets
        self.port_b = PortWidget("B", port_list, get_treadmill_data, treadmill)
        layout_port_b = PortGroupWidget.init_port_ui(self.port_b)

        # Port C Widgets
        self.port_c = PortWidget("C", port_list, get_treadmill_data, treadmill)
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
        layout_port.addWidget(port_widget.editLabel)
        layout_port.addWidget(port_widget.switchButton)
        layout_port.addWidget(port_widget.editTriggerDuration)
        layout_port.addWidget(port_widget.pulseButton)

        layout_port_position_trigger = QHBoxLayout()
        layout_port_position_trigger.addWidget(port_widget.pulseRepetitionButton)
        layout_port_position_trigger.addWidget(port_widget.editTriggerPosition)
        layout_port_position_trigger.addWidget(port_widget.editTriggerWindow)
        layout_port_position_trigger.addWidget(port_widget.editTriggerRetention)
        layout_port_position_trigger.addWidget(port_widget.setButton)
        layout_port_position_trigger.addWidget(port_widget.restoreButton)
        port_widget.groupboxPositionTrigger.setLayout(layout_port_position_trigger)
        port_widget.groupboxPositionTrigger.setChecked(False)

        layout_port.addWidget(port_widget.groupboxPositionTrigger)

        return layout_port
