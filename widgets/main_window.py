import sys
import os
from PyQt5 import QtWidgets
from PyQt5.QtCore import QSize, QThread, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QGridLayout, QSizePolicy, QSpacerItem, QWidget, QPushButton, QComboBox, QMessageBox, \
    QPlainTextEdit, QFileDialog, QHBoxLayout, QVBoxLayout
from model.treadmill_handler import Treadmill
from model.read_thread import ReadThread
from model.gtools import GTools
from widgets.plot_widget import PlotWidget
from widgets.port_group_widget import PortGroupWidget


class Window(QWidget):
    def __init__(self):
        # Window
        super().__init__()

        # INVISIBLE OBJECTS
        self.treadmill = Treadmill()
        self.treadmill.connection_signal.connect(self.treadmill_connection_handler)
        self.treadmill.init_signal.connect(self.change_plot_color)
        self.treadmill.record_signal.connect(self.change_plot_color)
        self.treadmill.record_signal.connect(self.update_record_button)
        self.treadmill.ls_alarm_signal.connect(self.ls_alarm_handler)

        # Read thread
        self.read_thread = ReadThread(self.treadmill)
        self.read_thread.worker.message_sig.connect(self.print_to_console)

        # List for storing connected treadmills
        self.treadmill_list = list()
        self.port_list = list()

        # Plot resources
        self.plot_timer = QTimer(self)
        self.plot_timer.timeout.connect(self.update_plot)

        self.init_ui()

        # Init folder & treadmills
        self.init_folder()
        self.get_treadmills()

    def init_ui(self):
        self.setWindowTitle('pyTreadmill')
        self.myicon = str(os.getcwd() + '/res/vinyl16.png')
        self.setWindowIcon(QIcon(self.myicon))

        # Button - Browse folders button
        self.browse_button = QPushButton('Set folder')
        self.browse_button.clicked.connect(self.select_folder)

        # Dropdown - For selecting treadmill
        self.treadmill_list_dropdown = QComboBox()

        # Button - Refresh treadmill list
        self.find_treadmills_button = QPushButton("")
        self.find_treadmills_button.setIcon(QIcon(os.getcwd() + '/res/refresh16.png'))
        self.find_treadmills_button.setIconSize(QSize(16, 16))
        self.find_treadmills_button.clicked.connect(self.get_treadmills)

        # Button - Connect button
        self.connect_button = QPushButton('Connect')
        self.connect_button.clicked.connect(self.connect_button_action)
        self.connect_button.setProperty("enabled", False)

        # plainTextEdit - Main console style display
        self.main_console = QPlainTextEdit()
        self.main_console.setObjectName("mainConsole")
        self.main_console.setProperty("readOnly", True)
        self.main_console.setMinimumHeight(100)

        # Ports
        self.ports_widget = PortGroupWidget(self.port_list, self.read_thread, self.treadmill)

        # Button - Record button
        self.record_button = QPushButton('Record')
        self.record_button.clicked.connect(self.record_button_action)
        self.record_button.setProperty("enabled", False)

        # Button - Reset button
        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(
            lambda: self.open_dialog("reset", lambda: self.treadmill.write_data("x")))
        self.reset_button.setProperty("enabled", False)

        # Button - Reinitialize button
        self.reinitialize_button = QPushButton("Reinitialize", self)
        self.reinitialize_button.clicked.connect(
            lambda: self.open_dialog("reinitialize", lambda: self.treadmill.write_data("i")))
        self.reinitialize_button.setProperty("enabled", False)

        # Plot
        self.plot_widget = PlotWidget()

        # Layouts
        level_one_layout = QHBoxLayout()
        level_one_layout.addWidget(self.browse_button)
        level_one_layout.addWidget(self.treadmill_list_dropdown)
        level_one_layout.addWidget(self.find_treadmills_button)
        level_one_layout.addWidget(self.connect_button)

        record_and_reset_layout = QGridLayout()
        for ndx in range(3):
            record_and_reset_layout.addItem(QSpacerItem(110, 10), 0, ndx)
        record_and_reset_layout.addWidget(self.reinitialize_button, 0, 3)
        record_and_reset_layout.addWidget(self.reset_button, 0, 4)
        record_and_reset_layout.addWidget(self.record_button, 0, 5)        

        main_layout = QVBoxLayout()
        main_layout.addLayout(level_one_layout)
        main_layout.addWidget(self.main_console)
        main_layout.addWidget(self.ports_widget)
        main_layout.addLayout(record_and_reset_layout)
        main_layout.addWidget(self.plot_widget)

        self.setLayout(main_layout)

        # FINALIZE
        self.show()
        self.setMaximumWidth(self.width())

    def open_dialog(self, question_object, callback):
        question_string = "Are you sure you want to {0}?".format(question_object)
        choice = QMessageBox.question(self, 'Message', question_string,
                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

        if choice == QMessageBox.Yes:
            callback()
        else:
            pass

    def check_connection_requirement(self):
        if len(self.treadmill_list) == 0 or self.read_thread.worker.save_folder is None:
            self.connect_button.setProperty("enabled", False)
        else:
            self.connect_button.setProperty("enabled", True)

    def init_folder(self):
        self.read_thread.worker.save_folder = GTools.get_save_folder()
        self.print_to_console(f"Save folder set to: {self.read_thread.worker.save_folder} \n")

    def select_folder(self):
        self.read_thread.worker.save_folder = str(QFileDialog.getExistingDirectory(self, "Select Directory"))

        if os.path.isdir(self.read_thread.worker.save_folder):
            GTools.update_save_folder(self.read_thread.worker.save_folder)
            self.print_to_console(f"Save folder set to: {self.read_thread.worker.save_folder} \n")
        else:
            self.read_thread.worker.save_folder = None
            self.print_to_console("No valid save folder was set.\n")

        self.check_connection_requirement()

    def get_treadmills(self):
        self.treadmill_list_dropdown.clear()
        self.treadmill_list = Treadmill.find_treadmills()
        self.treadmill_list_dropdown.addItems(self.treadmill_list)
        self.check_connection_requirement()

    def treadmill_connection_handler(self, connected):
        if connected:
            self.print_to_console("Serial connection established.\n")
            self.connect_button.setProperty("text", "Disconnect")
            self.reset_button.setProperty("enabled", True)
            self.reinitialize_button.setProperty("enabled", True)
            self.record_button.setProperty("enabled", True)
            self.read_thread.worker.port_list = self.port_list
            self.ports_widget.setEnabled(True)
            self.read_thread.start()
            self.enable_velocity_plot()
        else:
            self.print_to_console("Serial connection terminated.\n")
            if self.read_thread.isRunning():
                self.read_thread.stop()
            for port_data in self.port_list:
                port_data.port.groupbox_position_trigger.setChecked(False)
            self.connect_button.setProperty("text", "Connect")
            self.reset_button.setProperty("enabled", False)
            self.reinitialize_button.setProperty("enabled", False)
            self.record_button.setProperty("enabled", False)
            self.ports_widget.setEnabled(False)
            self.disable_velocity_plot()
            self.get_treadmills()

    def connect_button_action(self):
        if not self.read_thread.worker.running:
            self.print_to_console("Connecting to treadmill on port " +
                               self.treadmill_list_dropdown.currentData(0) + ".")
            self.treadmill.connect(self.treadmill_list_dropdown.currentData(0))
        else:
            self.read_thread.stop()
            self.treadmill.close_connection()

    def record_button_action(self):
        if self.treadmill.recording:
            self.treadmill.write_data("r")
        else:
            self.treadmill.write_data("R")

    def update_record_button(self, recording_state):
        if recording_state:
            self.record_button.setText("🔴 REC")
        else:
            self.record_button.setText("Record")

    def print_to_console(self, text):
        self.main_console.appendPlainText(text)

    def enable_velocity_plot(self):
        self.plot_widget.enable()
        self.plot_timer.start(5)

    def disable_velocity_plot(self):
        self.plot_timer.stop()
        self.plot_widget.disable()

    def update_plot(self):
        self.plot_widget.update_plot(self.read_thread.worker.treadmill_data, self.treadmill.recording)

    def change_plot_color(self):
        self.plot_widget.update_color(self.treadmill)

    def ls_alarm_handler(self, alarm_state):
        if alarm_state:
            self.print_to_console("Warning! Missmatch between lap sensor signal and encoder null position." +
            "Check Treadmill belt and reinitialize.\n")
            self.reinitialize_button.setStyleSheet("color: white; background-color: red;")
        else:
            self.reinitialize_button.setStyleSheet("color: black; background-color: white;")

    def close_application(self):
        choice = QMessageBox.question(self, 'Message',
                                      "Are you sure you want to quit?", QMessageBox.Yes |
                                      QMessageBox.No, QMessageBox.No)

        if choice == QMessageBox.Yes:
            sys.exit()
        else:
            pass
