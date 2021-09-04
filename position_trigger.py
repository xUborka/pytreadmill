from PyQt5.QtCore import pyqtSignal, QTimer, QObject


class PositionTriggerWorker(QObject):
    triggerSignal = pyqtSignal()
    finishedSignal = pyqtSignal()
    checkerInterval = 50

    def __init__(self, parent_trigger_data, parent=None):
        super().__init__(parent)
        self.position_trigger_data = parent_trigger_data

        self.is_running = True
        self.is_single_shot = True
        self.has_fired = False

        self.trigger_timer = QTimer(self)
        self.trigger_timer.setSingleShot(False)
        self.trigger_timer.timeout.connect(self.trigger)

        self.check_timer = QTimer(self)
        self.check_timer.setSingleShot(False)
        self.check_timer.timeout.connect(self.check_position)

    def process(self):
        self.has_fired = False
        self.check_timer.start(self.checkerInterval)

    def trigger(self):
        if self.is_single_shot:
            if not self.has_fired:
                self.triggerSignal.emit()
        else:
            self.triggerSignal.emit()
        self.has_fired = True

    def set_timer_single_shot(self, is_single_shot):
        self.is_single_shot = is_single_shot

    def update_trigger_interval(self):
        self.trigger_timer.setInterval(self.position_trigger_data.retention)

    def check_position(self):
        treadmill_data = self.position_trigger_data.port.treadmill_data.treadmill_data
        if self.position_trigger_data.start < treadmill_data.rel_position < \
           self.position_trigger_data.start + self.position_trigger_data.window:
            if not self.trigger_timer.isActive():
                self.trigger_timer.start(self.position_trigger_data.retention)
        else:
            self.has_fired = False
            self.trigger_timer.stop()

    def terminate(self):
        self.is_running = False
        self.has_fired = False
        self.check_timer.stop()
        self.trigger_timer.stop()
