import sys
import os
import time
from PyQt5 import QtWidgets
from PyQt5.QtCore import QSize, QThread, QTimer, QObject, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QGridLayout, QSizePolicy, QSpacerItem, QWidget, QPushButton, QComboBox, QMessageBox, \
    QPlainTextEdit, QFileDialog, QHBoxLayout, QVBoxLayout, QCheckBox, QLabel
from model.treadmill_handler import Treadmill
from model.read_thread import ReadThread
from model.gtools import GTools
from widgets.plot_widget import PlotWidget
from widgets.port_group_widget import PortGroupWidget


class Window(QWidget):
    def __init__(self):
        super().__init__()

        self.title = "Camera Stream"

        self.setWindowTitle(self.title)
        self.stream = QLabel(self)
        self.stream_thread = QThread(self)
        self.stream_worker: QObject

    @pyqtSlot(QImage)
    def set_image(self, image):
        self.stream.setPixmap(QPixmap.fromImage(image))