from ast import Gt
import os
from tkinter import Image
import pypylon.pylon as pypy
import numpy as np
from PyQt5.QtCore import QObject, pyqtSignal, QThread
import traceback
import imageio as iio
import time
from model.gtools import GTools

class Communicate(QObject):
    img_sig = pyqtSignal(np.ndarray) # or change it to whatever datatype/class the image will be
    grabbing_sig = pyqtSignal(bool)
    enable_vid_rec_sig = pyqtSignal(bool)
    rec_vid_sig = pyqtSignal(bool)


class ImageHandler(pypy.ImageEventHandler):
    def __init__(self, cam):
        super().__init__()
        # self.img = np.zeros((cam.Height.Value, cam.Width.Value), dtype=np.uint16) # maybe unnecessary
        self.com = Communicate()
        self.last_time = time.time()
        
    def OnImageGrabbed(self, camera, grabResult):
        try:
            if grabResult.GrabSucceeded():
                self.img = grabResult.Array
                self.com.img_sig.emit(self.img)
                # the above two lines can be merged into one if unsuccesful grabbing doesn't need handling for the output
                # self.com.img_sig.emit(grabResult.Array)

                fps = 1 / (time.time() - self.last_time)
                self.last_time = time.time()
                # print("fps: %.2f" % fps)
            else:
                raise RuntimeError("Grab Failed")
        except Exception as e:
            traceback.print_exc()

class BaslerCameraControl(QObject):
    def __init__(self):
        self.__setup_emulated_cam()
        self.cam = pypy.InstantCamera(pypy.TlFactory.GetInstance().CreateFirstDevice())
        self.handler = ImageHandler(self.cam)
        self.com = Communicate()

        self.vid_write_thread = VideoWriteThread(fps=30)
        self.vid_write_thread.start()
        self.com.grabbing_sig.connect(self.vid_write_thread.writer.external_stop)
        # talán a következő sorokra kell implementálni a rec_vid_sig-hez a videó indítását

        self.com.rec_vid_sig.connect(self.__setup_vid_rec) #jelenleg hibás megoldás (ez már nem csak setup)
        # ha kell video rec, akkor a grabbinget is el kell indítani, függetlenül attól, hogy van a stream window
        # tehát
        
    def __setup_emulated_cam(self):
        NUM_CAMERAS = 1
        os.environ["PYLON_CAMEMU"] = f"{NUM_CAMERAS}"

    def __setup_vid_rec(self, to_rec: bool):
        if to_rec:
            self.handler.com.img_sig.connect(self.vid_write_thread.writer.write)
        else:
            self.handler.com.img_sig.disconnect(self.vid_write_thread.writer.write)

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
        if self.cam.IsOpen() and not self.cam.IsGrabbing():
            self.cam.StartGrabbing(pypy.GrabStrategy_LatestImages, pypy.GrabLoop_ProvidedByInstantCamera)
            if self.cam.IsGrabbing():
                self.com.grabbing_sig.emit(True)
        
        self.vid_write_thread.writer.start_writing()

    def stop_grabbing(self):
        self.cam.StopGrabbing()
        self.__unset_handler()
        if not self.cam.IsGrabbing():
            self.com.grabbing_sig.emit(False)
            print("camera grabbing: " + str(self.cam.IsGrabbing()))

class VideoWriter(QObject):
    finished = pyqtSignal()

    def __init__(self, fps=30) -> None:
        super().__init__()
        self.concrete_writer: iio.core.format.Writer = None
        self.fps: int = fps
        self.is_writing = False
        self.last_rec_time = self.__millisecs()

    def set_writer(self, vid_path: str=None):
        if vid_path == None:
            save_folder = GTools.get_save_folder()
            start_date = time.strftime("%Y-%m-%d %H_%M_%S")
            vid_path = save_folder + '/' + start_date

        self.concrete_writer = self.__get_mp4_writer(vid_path)

    def start_writing(self):
        if self.concrete_writer == None:
            self.set_writer()
        self.is_writing = True
        print("start writing")
    
    def write(self, img):
        if self.is_writing and self.__max_fps_ok():
            self.last_rec_time = self.__millisecs()
            self.concrete_writer.append_data(img)

    def stop_writing(self):
        if self.is_writing:
            self.concrete_writer.close()
            print("Video writing finished.")
            self.finished.emit()

    def external_stop(self, is_grabbing):
        if not is_grabbing:
            # print("I want to stop and bool is: " + str(is_grabbing))
            self.stop_writing()

    def __millisecs(self) -> int:
        return int(time.time() * 1000)

    def __max_fps_ok(self) -> bool:
        return ((self.__millisecs() - self.last_rec_time) > (1 / self.fps))

    def __get_mp4_writer(self, vid_path: str):
        fname = str(vid_path + ".mp4")
        return iio.get_writer(fname, format='FFMPEG', fps=self.fps, codec='libx264', quality=4) # mode='I'

class VideoWriteThread(QThread):
    terminate_sig = pyqtSignal()

    def __init__(self, fps=30, parent=None):
        super().__init__(parent=parent)
        self.writer = VideoWriter(fps)
        self.writer.moveToThread(self)
        self.started.connect(self.writer.set_writer)
        self.writer.finished.connect(self.quit)
        self.terminate_sig.connect(self.writer.stop_writing)
        
    def stop(self):
        self.terminate_sig.emit()