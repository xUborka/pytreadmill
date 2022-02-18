from tkinter import Image
import pypylon.pylon as pypy
import numpy as np
from PyQt5.QtCore import QObject, pyqtSignal
import traceback

class Communicate(QObject):
    img_sig = pyqtSignal(np.ndarray) # or change it to whatever datatype/class the image will be

class ImageHandler(pypy.ImageEventHandler):
    def __init__(self, cam):
        super().__init__()
        # self.img = np.zeros((cam.Height.Value, cam.Width.Value), dtype=np.uint16) # maybe unnecessary
        self.com = Communicate()
        
    def OnImageGrabbed(self, camera, grabResult):
        try:
            if grabResult.GrabSucceeded():
                self.img = grabResult.Array
                self.com.img_sig.emit(self.img)
                # the above two lines can be merged into one if unsuccesful grabbing doesn't need handling for the output
                # self.com.img_sig.emit(grabResult.Array)
            else:
                raise RuntimeError("Grab Failed")
        except Exception as e:
            traceback.print_exc()

class BaslerCameraControl():
    def __init__(self):
        self.cam = pypy.InstantCamera(pypy.TlFactory.GetInstance().CreateFirstDevice())
        self.handler = ImageHandler(self.cam)

    def __set_default_settings(self, cam):
        cam.UserSetSelector = "Default"
        cam.UserSetLoad.Execute()

    def __set_handler(self):
        # self.handler = ImageHandler()
        self.cam.RegisterImageEventHandler(self.handler , pypy.RegistrationMode_ReplaceAll, pypy.Cleanup_None)

    def __unset_handler(self):
        self.cam.DeregisterImageEventHandler(self.handler)

    def connect_first_cam(self):
        # self.cam = pypy.InstantCamera(pypy.TlFactory.GetInstance().CreateFirstDevice())
        if self.cam.IsPylonDeviceAttached():
            self.cam.Open()
            self.__set_default_settings(self.cam)
            print("Camera connected")
        else:
            print("No device found")

    def connect_cam(self, id):
        """Implement if there will be more than one Basler cameras connected to the system"""
        pass

    def close_cam(self):
        self.cam.Close()

    def start_grabbing(self):
        self.__set_handler()
        self.cam.StartGrabbing(pypy.GrabStrategy_LatestImages, pypy.GrabLoop_ProvidedByInstantCamera)

    def stop_grabbing(self):
        self.cam.StopGrabbing()
        self.__unset_handler()