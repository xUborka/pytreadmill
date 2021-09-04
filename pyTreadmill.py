import sys
import os
from PyQt5.QtCore import QSize, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QPushButton, QComboBox, QMessageBox, \
    QPlainTextEdit, QFileDialog, QHBoxLayout, QVBoxLayout
from Treadmill import Treadmill
from ReadThreadClass import ReadThreadClass
from gtools import GTools
from widgets.plot_widget import PlotWidget
from widgets.port_widget import PortWidget


class Window(QWidget):
    def __init__(self):
        # Window
        super(Window, self).__init__()

        # INVISIBLE OBJECTS
        self.treadmill = Treadmill()
        self.treadmill.connectionSignal.connect(self.treadmillConnectionHandler)
        self.treadmill.initializationSignal.connect(self.change_plot_color)
        self.treadmill.recordSignal.connect(self.change_plot_color)

        # Read thread
        self.readThread = ReadThreadClass(self.treadmill)
        self.readThread.printDataSignal.connect(self.printTreadmillData)
        self.readThread.messageSignal.connect(self.print2Console)
        self.readThread.treadmillStateChanged.connect(self.change_plot_color)

        # List for storing connected treadmills
        self.treadmillList = list()
        self.portList = list()

        # Plot resources
        self.plotTimer = QTimer(self)
        self.plotTimer.timeout.connect(self.update_plot)

        self.initUI()

        # Init folder & treadmills
        self.init_folder()
        self.getTreadmills()

    def initUI(self):
        self.setWindowTitle('pyTreadmill')
        self.myicon = str(os.getcwd() + '/res/vinyl16.png')
        self.setWindowIcon(QIcon(self.myicon))

        # Button - Browse folders button
        self.browseButton = QPushButton('Set folder')
        self.browseButton.clicked.connect(self.selectFolder)

        # Dropdown - For selecting treadmill
        self.treadmillListDropdown = QComboBox()

        # Button - Refresh treadmill list
        self.findTreadmillsButton = QPushButton("")
        self.findTreadmillsButton.setIcon(QIcon(os.getcwd() + '/res/refresh16.png'))
        self.findTreadmillsButton.setIconSize(QSize(16, 16))
        self.findTreadmillsButton.clicked.connect(self.getTreadmills)

        # Button - Connect button
        self.connectButton = QPushButton('Connect')
        self.connectButton.clicked.connect(self.connectButtonAction)
        self.connectButton.setProperty("enabled", False)

        # plainTextEdit - Main console style display
        self.mainConsole = QPlainTextEdit()
        self.mainConsole.setObjectName("mainConsole")
        self.mainConsole.setProperty("readOnly", True)
        self.mainConsole.setMinimumHeight(100)

        # Ports
        self.ports_widget = PortWidget(self.portList, self.readThread, self.treadmill)

        self.treadmillDataPrinter = QPlainTextEdit()
        self.treadmillDataPrinter.setObjectName("treadmillData")
        self.treadmillDataPrinter.setProperty("readOnly", True)
        self.treadmillDataPrinter.setOverwriteMode(True)
        self.treadmillDataPrinter.setMaximumHeight(30)

        # Plot
        self.plotWidget = PlotWidget()

        levelOneLayout = QHBoxLayout()
        levelOneLayout.addWidget(self.browseButton)
        levelOneLayout.addWidget(self.treadmillListDropdown)
        levelOneLayout.addWidget(self.findTreadmillsButton)
        levelOneLayout.addWidget(self.connectButton)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(levelOneLayout)
        mainLayout.addWidget(self.mainConsole)
        mainLayout.addWidget(self.ports_widget)
        mainLayout.addWidget(self.plotWidget)

        self.setLayout(mainLayout)

        # FINALIZE
        self.show()
        self.setMaximumWidth(self.width())

    def openDialog(self, questionObject, callback):
        questionString = "Are you sure you want to {0}?".format(questionObject)
        choice = QMessageBox.question(self, 'Message', questionString,
                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

        if choice == QMessageBox.Yes:
            callback()
        else:
            pass

    def checkConnectRequirement(self):
        if len(self.treadmillList) == 0 or self.readThread.saveFolder is None:
            self.connectButton.setProperty("enabled", False)
        else:
            self.connectButton.setProperty("enabled", True)

    def init_folder(self):
        self.readThread.saveFolder = os.getcwd()
        self.print2Console(f"Save folder set to: {self.readThread.saveFolder} \n")

    def selectFolder(self):
        self.readThread.saveFolder = str(QFileDialog.getExistingDirectory(self, "Select Directory"))

        if os.path.isdir(self.readThread.saveFolder):
            GTools.updateSaveFolder(self.readThread.saveFolder)
            self.print2Console(f"Save folder set to: {self.readThread.saveFolder} \n")
        else:
            self.readThread.saveFolder = None
            self.print2Console("No valid save folder was set.")

        self.checkConnectRequirement()

    def getTreadmills(self):
        self.treadmillListDropdown.clear()
        self.treadmillList = Treadmill.findTreadmills()
        self.treadmillListDropdown.addItems(self.treadmillList)
        self.checkConnectRequirement()

    def treadmillConnectionHandler(self, connected):
        if connected:
            self.print2Console("Serial connection established.\n")
            self.readThread.running = True
            self.connectButton.setProperty("text", "Disconnect")
            self.readThread.portList = self.portList
            self.ports_widget.setEnabled(True)
            self.readThread.start()
            self.enableVelocityPlot()
        else:
            self.print2Console("Serial connection terminated.\n")
            self.readThread.running = False
            self.connectButton.setProperty("text", "Connect")
            self.ports_widget.setEnabled(False)
            self.disableVelocityPlot()
            self.getTreadmills()

    def connectButtonAction(self):
        if not self.readThread.running:
            self.print2Console("Connecting to treadmill on port " +
                               self.treadmillListDropdown.currentData(0) + ".")
            self.treadmill.connect(self.treadmillListDropdown.currentData(0))
        else:
            self.treadmill.closeConnection()

    def printTreadmillData(self, text):
        self.treadmillDataPrinter.setPlainText(text)

    def print2Console(self, text):
        self.mainConsole.appendPlainText(text)

    def enableVelocityPlot(self):
        self.plotWidget.enable()
        self.plotTimer.start(5)

    def disableVelocityPlot(self):
        self.plotTimer.stop()
        self.plotWidget.disable()

    def update_plot(self):
        self.plotWidget.update_plot(self.readThread.treadmillData, self.treadmill.recording)

    def change_plot_color(self):
        self.plotWidget.update_color(self.treadmill)

    def close_application(self):
        choice = QMessageBox.question(self, 'Message',
                                      "Are you sure you want to quit?", QMessageBox.Yes |
                                      QMessageBox.No, QMessageBox.No)

        if choice == QMessageBox.Yes:
            sys.exit()
        else:
            pass
