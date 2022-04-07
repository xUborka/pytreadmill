from PyQt5 import QtGui
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QLabel, QMainWindow

from model.basler_cam_handler import BaslerCameraControl
import numpy as np

class CamStreamWindow(QMainWindow):
    def __init__(self, cam_control: BaslerCameraControl):
        super().__init__()

        self.cam_control = cam_control
        self.cam_control.handler.com.img_sig.connect(self.paint_event)

        self.title = "Camera Stream"
        self.setWindowTitle(self.title)
        self.setGeometry(0, 0, 400, 300)

        self.stream = QLabel(self)
        self.stream.setText("Label is here")
        self.stream.setMinimumSize(1, 1)

        self.setCentralWidget(self.stream)

        # self.stream_thread = QThread(self)
        # self.stream_worker: QObject

    @pyqtSlot(np.ndarray)
    def paint_event(self, image: np.ndarray):
        img = QImage(image, image.shape[1], image.shape[0], QImage.Format_Grayscale8)
        pixmap = QPixmap(img).scaled(self.width(), self.height(), Qt.KeepAspectRatio)
        self.stream.setPixmap(pixmap)

        ### dummy testing
        # imarray = np.random.rand(1024,768,3) * 255
        # qimage = QImage(imarray, imarray.shape[1], imarray.shape[0], QImage.Format_RGB888)    
        # self.stream.setPixmap(QPixmap(qimage))

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.cam_control.stop_grabbing()
        return super().closeEvent(a0)
        