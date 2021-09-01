
class PositionTriggerData:
    def __init__(self, port=None):
        self.port = port
        self.is_active = False

        self.start = 0
        self.window = 0
        self.retention = 0
        self.duration = 0
