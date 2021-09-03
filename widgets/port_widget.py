from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QGroupBox
from Port import Port

class PortWidget(QGroupBox):
    def __init__(self, port_list, readThread, treadmill):
        super().__init__("Port Settings")
        self.port_a = Port("A", port_list, readThread, treadmill)
        layout_port_a = PortWidget.init_port_ui(self.port_a)

        # Port B Widgets
        self.port_b = Port("B", port_list, readThread, treadmill)
        layout_port_b = PortWidget.init_port_ui(self.port_b)

        # Port C Widgets
        self.port_c = Port("C", port_list, readThread, treadmill)
        layout_port_c = PortWidget.init_port_ui(self.port_c)

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