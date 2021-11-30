
class TreadmillData:
    def __init__(self, t: int = 0, rec: int = -1,
                 vel: int = 0, abs_pos: int = 0,
                 lap: int = 0, rel_pos: int = 0,
                 lick: int = 0, init: int = 0,
                 port_states: list = [0, 0, 0],
                 lap_sensor_alarm = 0):
        self.time = int(t)
        self.recording = int(rec)
        self.velocity = int(vel)
        self.abs_position = int(abs_pos)
        self.lap = int(lap)
        self.rel_position = int(rel_pos)
        self.lick = int(lick)
        self.initialized = int(init)
        self.port_states = list(map(int, port_states))
        self.lap_sensor_alarm = int(lap_sensor_alarm)

    def invalidate(self):
        self.time = 0
        self.recording = -1
        self.velocity = 0
        self.abs_position = 0
        self.lap = 0
        self.rel_position = 0
        self.lick = 0
        self.initialized = 0
        self.port_states = [0, 0, 0]
        self.lap_sensor_alarm = 0

    def __str__(self) -> str:
        return ', '.join(map(str, [self.time, self.velocity, self.abs_position, self.lap, self.rel_position, self.lick]))
