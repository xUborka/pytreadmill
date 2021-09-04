import sys
import os
from PyQt5.QtCore import QSize, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QPushButton, QComboBox, QMessageBox, \
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

        # Read thread
        self.read_thread = ReadThread(self.treadmill)
        self.read_thread.print_data_signal.connect(self.print_treadmill_data)
        self.read_thread.message_signal.connect(self.print_to_console)
        self.read_thread.treadmill_state_changed.connect(self.change_plot_color)

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

        self.treadmill_data_printer = QPlainTextEdit()
        self.treadmill_data_printer.setObjectName("treadmillData")
        self.treadmill_data_printer.setProperty("readOnly", True)
        self.treadmill_data_printer.setOverwriteMode(True)
        self.treadmill_data_printer.setMaximumHeight(30)

        # Plot
        self.plot_widget = PlotWidget()

        level_one_layout = QHBoxLayout()
        level_one_layout.addWidget(self.browse_button)
        level_one_layout.addWidget(self.treadmill_list_dropdown)
        level_one_layout.addWidget(self.find_treadmills_button)
        level_one_layout.addWidget(self.connect_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(level_one_layout)
        main_layout.addWidget(self.main_console)
        main_layout.addWidget(self.ports_widget)
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
        if len(self.treadmill_list) == 0 or self.read_thread.save_folder is None:
            self.connect_button.setProperty("enabled", False)
        else:
            self.connect_button.setProperty("enabled", True)

    def init_folder(self):
        self.read_thread.save_folder = GTools.get_save_folder()
        self.print_to_console(f"Save folder set to: {self.read_thread.save_folder} \n")

    def select_folder(self):
        self.read_thread.save_folder = str(QFileDialog.getExistingDirectory(self, "Select Directory"))

        if os.path.isdir(self.read_thread.save_folder):
            GTools.update_save_folder(self.read_thread.save_folder)
            self.print_to_console(f"Save folder set to: {self.read_thread.save_folder} \n")
        else:
            self.read_thread.save_folder = None
            self.print_to_console("No valid save folder was set.")

        self.check_connection_requirement()

    def get_treadmills(self):
        self.treadmill_list_dropdown.clear()
        self.treadmill_list = Treadmill.find_treadmills()
        self.treadmill_list_dropdown.addItems(self.treadmill_list)
        self.check_connection_requirement()

    def treadmill_connection_handler(self, connected):
        if connected:
            self.print_to_console("Serial connection established.\n")
            self.read_thread.running = True
            self.connect_button.setProperty("text", "Disconnect")
            self.read_thread.port_list = self.port_list
            self.ports_widget.setEnabled(True)
            self.read_thread.start()
            self.enable_velocity_plot()
        else:
            self.print_to_console("Serial connection terminated.\n")
            self.read_thread.running = False
            self.connect_button.setProperty("text", "Connect")
            self.ports_widget.setEnabled(False)
            self.disable_velocity_plot()
            self.get_treadmills()

    def connect_button_action(self):
        if not self.read_thread.running:
            self.print_to_console("Connecting to treadmill on port " +
                               self.treadmill_list_dropdown.currentData(0) + ".")
            self.treadmill.connect(self.treadmill_list_dropdown.currentData(0))
        else:
            self.treadmill.close_connection()

    def print_treadmill_data(self, text):
        self.treadmill_data_printer.setPlainText(text)

    def print_to_console(self, text):
        self.main_console.appendPlainText(text)

    def enable_velocity_plot(self):
        self.plot_widget.enable()
        self.plot_timer.start(5)

    def disable_velocity_plot(self):
        self.plot_timer.stop()
        self.plot_widget.disable()

    def update_plot(self):
        self.plot_widget.update_plot(self.read_thread.treadmill_data, self.treadmill.recording)

    def change_plot_color(self):
        self.plot_widget.update_color(self.treadmill)

    def close_application(self):
        choice = QMessageBox.question(self, 'Message',
                                      "Are you sure you want to quit?", QMessageBox.Yes |
                                      QMessageBox.No, QMessageBox.No)

        if choice == QMessageBox.Yes:
            sys.exit()
        else:
            pass