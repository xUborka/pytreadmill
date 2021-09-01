
class TreadmillData:
    def __init__(self, t: int = 0, rec: int = -1,
                 vel: int = 0, abs_pos: int = 0,
                 lap: int = 0, rel_pos: int = 0,
                 lick: int = 0, init: int = 0,
                 port_states: list = [0, 0, 0]):
        self.time = int(t)
        self.recording = int(rec)
        self.velocity = int(vel)
        self.absPosition = int(abs_pos)
        self.lap = int(lap)
        self.relPosition = int(rel_pos)
        self.lick = int(lick)
        self.initialized = int(init)
        self.portStates = list(map(int, port_states))

    def invalidate(self):
        self.time = 0
        self.recording = -1
        self.velocity = 0
        self.absPosition = 0
        self.lap = 0
        self.relPosition = 0
        self.lick = 0
        self.initialized = 0
        self.portStates = [0, 0, 0]

    def __str__(self) -> str:
        return ','.join(map(str, [self.time, self.velocity, self.absPosition, self.lap, self.relPosition, self.lick]))
