import sys
import os
import time
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QSize, QThread, QTimer, QObject, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QGridLayout, QSizePolicy, QSpacerItem, QWidget, QPushButton, QComboBox, QMessageBox, \
    QPlainTextEdit, QFileDialog, QHBoxLayout, QVBoxLayout, QCheckBox, QLabel, QMainWindow
from model.treadmill_handler import Treadmill
from model.read_thread import ReadThread
from model.gtools import GTools
from widgets.plot_widget import PlotWidget
from widgets.port_group_widget import PortGroupWidget

from model.basler_cam_handler import BaslerCameraControl
import numpy as np

# import matplotlib
# matplotlib.use("Qt5Agg")
# import matplotlib.pyplot as plt


class CamStreamWindow(QMainWindow):
    def __init__(self, cam_control: BaslerCameraControl):
        super().__init__()

        self.cam_control = cam_control
        self.cam_control.handler.com.img_sig.connect(self.paint_event)

        # todo: add close event to stop grabbing

        self.title = "Camera Stream"
        self.setWindowTitle(self.title)
        self.setGeometry(0, 0, 400, 300)

        self.stream = QLabel(self)
        self.stream.setText("Label is here")

        self.setCentralWidget(self.stream)

        # self.stream_thread = QThread(self)
        # self.stream_worker: QObject

    @pyqtSlot(np.ndarray)
    def paint_event(self, image: np.ndarray):
        print(image.shape)
        print(self.geometry())
        img = QImage(image, image.shape[1], image.shape[0], QImage.Format_Grayscale8)
        pixmap = QPixmap(img).scaled(400, 300, Qt.KeepAspectRatio)
        self.stream.setPixmap(pixmap)

        ### dummy testing
        # imarray = np.random.rand(1024,768,3) * 255
        # qimage = QImage(imarray, imarray.shape[1], imarray.shape[0], QImage.Format_RGB888)    
        # self.stream.setPixmap(QPixmap(qimage))
        