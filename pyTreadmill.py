import sys
import os
from PyQt5.QtCore import QSize, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QComboBox, QMessageBox, \
    QPlainTextEdit, QFileDialog, QHBoxLayout, QVBoxLayout, QGroupBox
from Treadmill import Treadmill
from Port import Port
from ReadThreadClass import ReadThreadClass
from gtools import GTools
import pyqtgraph as pg
import numpy as np
import time


class Window(QWidget):
    plotPenWidth = 3

    def __init__(self):
        # Window
        super(Window, self).__init__()

        # INVISIBLE OBJECTS
        self.treadmill = Treadmill()
        self.treadmill.connectionSignal.connect(self.treadmillConnectionHandler)
        self.treadmill.initializationSignal.connect(self.changePlotColor)
        self.treadmill.recordSignal.connect(self.changePlotColor)

        # Read thread
        self.readThread = ReadThreadClass(self.treadmill)
        self.readThread.printDataSignal.connect(self.printTreadmillData)
        self.readThread.messageSignal.connect(self.print2Console)
        self.readThread.treadmillStateChanged.connect(self.changePlotColor)

        # List for storing connected treadmills
        self.treadmillList = []
        self.portList = list()

        # Plot resources
        self.velocityPlotList = np.zeros(1000)
        self.plotTimer = QTimer(self)
        self.plotTimer.timeout.connect(self.updatePlot)

        self.initUI()

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
        findTreadmillsButton = QPushButton("", )
        findTreadmillsButton.setIcon(QIcon(os.getcwd() + '/res/refresh16.png'))
        findTreadmillsButton.setIconSize(QSize(16, 16))
        findTreadmillsButton.clicked.connect(self.getTreadmills)

        # Button - Connect button
        self.connectButton = QPushButton('Connect')
        self.connectButton.clicked.connect(self.connectButtonAction)
        self.connectButton.setProperty("enabled", False)

        # plainTextEdit - Main console style display
        self.mainConsole = QPlainTextEdit()
        self.mainConsole.setObjectName("mainConsole")
        self.mainConsole.setProperty("readOnly", True)
        self.mainConsole.setMinimumHeight(100)

        # -------- A, B, C ports settings --------
        # Port A Widgets
        self.portA = Port("A", self.appendPortList, self.readThread.getTreadmillData, self.treadmill)
        self.portA.setSpinBox("triggerDuration", 100, 5000, 100, 100)
        self.portA.setSpinBox("triggerPosition", 1, 1000, 500, 50)
        self.portA.setSpinBox("triggerWindow", 0, 999, 100, 50)
        self.portA.setSpinBox("triggerRetention", 50, 10000, 3000, 500)
        # self.portA.positionTriggerChangedSignal.connect(self.readthread.updatePositionTriggerData)

        # Port A Layout
        layoutPortA = QHBoxLayout()
        layoutPortA.addWidget(self.portA.label)
        layoutPortA.addWidget(self.portA.editLabel)
        layoutPortA.addWidget(self.portA.switchButton)
        layoutPortA.addWidget(self.portA.editTriggerDuration)
        layoutPortA.addWidget(self.portA.pulseButton)

        layoutPortAPositionTrigger = QHBoxLayout()
        layoutPortAPositionTrigger.addWidget(self.portA.pulseRepetitionButton)
        layoutPortAPositionTrigger.addWidget(self.portA.editTriggerPosition)
        layoutPortAPositionTrigger.addWidget(self.portA.editTriggerWindow)
        layoutPortAPositionTrigger.addWidget(self.portA.editTriggerRetention)
        layoutPortAPositionTrigger.addWidget(self.portA.setButton)
        layoutPortAPositionTrigger.addWidget(self.portA.restoreButton)
        self.portA.groupboxPositionTrigger.setLayout(layoutPortAPositionTrigger)
        self.portA.groupboxPositionTrigger.setChecked(False)

        layoutPortA.addWidget(self.portA.groupboxPositionTrigger)

        # Port B Widgets
        self.portB = Port("B", self.appendPortList, self.readThread.getTreadmillData, self.treadmill)
        self.portB.setSpinBox("triggerDuration", 100, 5000, 100, 100)
        self.portB.setSpinBox("triggerPosition", 1, 1000, 500, 50)
        self.portB.setSpinBox("triggerWindow", 0, 999, 100, 50)
        self.portB.setSpinBox("triggerRetention", 50, 10000, 3000, 500)
        # self.portB.positionTriggerChangedSignal.connect(self.readthread.updatePositionTriggerData)

        # Port B Layout
        layoutPortB = QHBoxLayout()
        layoutPortB.addWidget(self.portB.label)
        layoutPortB.addWidget(self.portB.editLabel)
        layoutPortB.addWidget(self.portB.switchButton)
        layoutPortB.addWidget(self.portB.editTriggerDuration)
        layoutPortB.addWidget(self.portB.pulseButton)

        layoutPortBPositionTrigger = QHBoxLayout()
        layoutPortBPositionTrigger.addWidget(self.portB.pulseRepetitionButton)
        layoutPortBPositionTrigger.addWidget(self.portB.editTriggerPosition)
        layoutPortBPositionTrigger.addWidget(self.portB.editTriggerWindow)
        layoutPortBPositionTrigger.addWidget(self.portB.editTriggerRetention)
        layoutPortBPositionTrigger.addWidget(self.portB.setButton)
        layoutPortBPositionTrigger.addWidget(self.portB.restoreButton)
        self.portB.groupboxPositionTrigger.setLayout(layoutPortBPositionTrigger)
        self.portB.groupboxPositionTrigger.setChecked(False)

        layoutPortB.addWidget(self.portB.groupboxPositionTrigger)

        # Port C Widgets
        self.portC = Port("C", self.appendPortList, self.readThread.getTreadmillData, self.treadmill)
        self.portC.setSpinBox("triggerDuration", 100, 5000, 100, 100)
        self.portC.setSpinBox("triggerPosition", 1, 1000, 500, 50)
        self.portC.setSpinBox("triggerWindow", 0, 999, 100, 50)
        self.portC.setSpinBox("triggerRetention", 50, 10000, 3000, 500)
        # self.portC.positionTriggerChangedSignal.connect(self.readthread.updatePositionTriggerData)

        # Port C Layout
        layoutPortC = QHBoxLayout()
        layoutPortC.addWidget(self.portC.label)
        layoutPortC.addWidget(self.portC.editLabel)
        layoutPortC.addWidget(self.portC.switchButton)
        layoutPortC.addWidget(self.portC.editTriggerDuration)
        layoutPortC.addWidget(self.portC.pulseButton)

        layoutPortCPositionTrigger = QHBoxLayout()
        layoutPortCPositionTrigger.addWidget(self.portC.pulseRepetitionButton)
        layoutPortCPositionTrigger.addWidget(self.portC.editTriggerPosition)
        layoutPortCPositionTrigger.addWidget(self.portC.editTriggerWindow)
        layoutPortCPositionTrigger.addWidget(self.portC.editTriggerRetention)
        layoutPortCPositionTrigger.addWidget(self.portC.setButton)
        layoutPortCPositionTrigger.addWidget(self.portC.restoreButton)
        self.portC.groupboxPositionTrigger.setLayout(layoutPortCPositionTrigger)
        self.portC.groupboxPositionTrigger.setChecked(False)

        layoutPortC.addWidget(self.portC.groupboxPositionTrigger)

        # Layout for All Port Layouts
        layoutAllPorts = QVBoxLayout()
        layoutAllPorts.addLayout(layoutPortA)
        layoutAllPorts.addLayout(layoutPortB)
        layoutAllPorts.addLayout(layoutPortC)

        # layoutAllPorts = QGridLayout()

        groupboxAllPorts = QGroupBox("Port settings")
        groupboxAllPorts.setLayout(layoutAllPorts)

        self.containerArduinoIO = QWidget()
        self.layoutArduinoIO = QHBoxLayout(self.containerArduinoIO)
        self.layoutArduinoIO.addWidget(groupboxAllPorts)
        # self.layoutArduinoIO.addLayout(layout_RewardAndReset)
        # self.containerArduinoIO.setEnabled(False)

        self.treadmillDataPrinter = QPlainTextEdit()
        self.treadmillDataPrinter.setObjectName("treadmillData")
        self.treadmillDataPrinter.setProperty("readOnly", True)
        self.treadmillDataPrinter.setOverwriteMode(True)
        self.treadmillDataPrinter.setMaximumHeight(30)

        self.plotWidget = pg.PlotWidget(name='velocity plot')
        self.plotWidget.setMinimumSize(self.plotWidget.minimumWidth(), 300)
        self.plotWidget.setEnabled(False)
        self.velocityCurve = self.plotWidget.plot()
        self.velocityCurve.setPen(color='y', width=self.plotPenWidth)
        # self.plotWidget.enableMouse(True)
        self.plotWidget.setYRange(-20, 20)
        self.plotWidget.setLabel('left', 'velocity', '-')
        self.plotWidget.showAxis('bottom', False)
        self.plotWidget.showGrid(x=True, y=True)
        self.plotText = pg.TextItem(text='test', color='w', anchor=(1, 1.5))
        self.plotWidget.addItem(self.plotText)

        levelOneLayout = QHBoxLayout()
        levelOneLayout.addWidget(self.browseButton)
        levelOneLayout.addWidget(self.treadmillListDropdown)
        levelOneLayout.addWidget(findTreadmillsButton)
        levelOneLayout.addWidget(self.connectButton)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(levelOneLayout)
        mainLayout.addWidget(self.mainConsole)
        mainLayout.addWidget(self.containerArduinoIO)
        # mainLayout.addWidget(self.treadmillDataPrinter)
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

    def selectFolder(self):
        path = GTools.SAVE_FOLDER_PATH
        with open(path, 'r') as file:
            saveFolder = file.read()
        if os.path.isdir(saveFolder):
            self.readThread.saveFolder = str(QFileDialog.getExistingDirectory(self, "Select Directory", saveFolder))
        else:
            self.readThread.saveFolder = str(QFileDialog.getExistingDirectory(self, "Select Directory"))

        if self.readThread.saveFolder:
            GTools.updateSaveFolder(self.readThread.saveFolder)
            self.print2Console("Save folder set to: \n " + self.readThread.saveFolder + "\n")
        else:
            self.readThread.saveFolder = None
            self.print2Console("No valid save folder was set.")

        self.checkConnectRequirement()

    def getTreadmills(self):
        self.treadmillList = Treadmill.findTreadmills()

        self.treadmillListDropdown.clear()
        self.treadmillListDropdown.addItems(self.treadmillList)

        self.checkConnectRequirement()

    def treadmillConnectionHandler(self, connected):
        if connected:
            self.print2Console("Serial connection established.\n")
            self.readThread.running = True
            self.connectButton.setProperty("text", "Disconnect")
            self.containerArduinoIO.setEnabled(True)
            self.readThread.portList = self.portList
            self.readThread.start()
            self.enableVelocityPlot(True)
        else:
            self.print2Console("Serial connection terminated.\n")
            self.readThread.running = False
            self.connectButton.setProperty("text", "Connect")
            self.containerArduinoIO.setEnabled(False)
            self.enableVelocityPlot(False)
            self.getTreadmills()

    def connectButtonAction(self):
        if not self.readThread.running:
            self.print2Console("Connecting to treadmill on port " + self.treadmillListDropdown.currentData(0) + ".")
            self.treadmill.connect(self.treadmillListDropdown.currentData(0))
        else:
            self.treadmill.closeConnection()

    def printTreadmillData(self, text):
        self.treadmillDataPrinter.setPlainText(text)

    def print2Console(self, text):
        self.mainConsole.appendPlainText(text)

    def appendPortList(self, positionTriggerData):
        self.portList.append(positionTriggerData)

    def updateVelocityPlotList(self):
        self.velocityPlotList[:-1] = self.velocityPlotList[1:]
        self.velocityPlotList[-1] = self.readThread.treadmillData.velocity

    def enableVelocityPlot(self, enable):
        if enable:
            self.plotWidget.setEnabled = True
            self.velocityCurve.setData(self.velocityPlotList)
            self.plotTimer.start(5)
        else:
            self.plotTimer.stop()
            self.plotWidget.setEnabled = False

    def updatePlot(self):
        self.updateVelocityPlotList()
        self.velocityCurve.setData(self.velocityPlotList)
        self.velocityCurve.setPos(-1000, 0)
        self.updatePlotText()

    def updatePlotText(self):
        treadmillTime = time.strftime("%M:%S", time.gmtime(int(self.readThread.treadmillData.time) / 1000))
        tmpPlotText = str("time: " + treadmillTime + "\n" +
                          "velocity: " + str(self.readThread.treadmillData.velocity) + "\n" +
                          "abs. position: " + str(self.readThread.treadmillData.absPosition) + "\n" +
                          "lap: " + str(self.readThread.treadmillData.lap) + "\n" +
                          "rel. position: " + str(self.readThread.treadmillData.relPosition) + "\n")
        if self.treadmill.recording:
            tmpPlotText = str(tmpPlotText + "🔴 REC")
        self.plotText.setText(text=tmpPlotText)

    def changePlotColor(self):
        if self.treadmill.initialized:
            if self.treadmill.recording:
                self.velocityCurve.setPen(color='r', width=self.plotPenWidth)
            else:
                self.velocityCurve.setPen(color='w', width=self.plotPenWidth)
        else:
            self.velocityCurve.setPen(color='y', width=self.plotPenWidth)

    def closeApplication(self):
        choice = QMessageBox.question(self, 'Message',
                                      "Are you sure you want to quit?", QMessageBox.Yes |
                                      QMessageBox.No, QMessageBox.No)

        if choice == QMessageBox.Yes:
            # print('quit application')
            sys.exit()
        else:
            pass


if __name__ == "__main__":  # had to add this otherwise app crashed
    app = QApplication(sys.argv)
    Gui = Window()
    sys.exit(app.exec_())
