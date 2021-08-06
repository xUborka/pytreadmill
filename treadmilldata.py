
class TreadmillData:
    def __init__(self, t=None, rec=None, vel=None, abs_pos=None, lap=None, rel_pos=None, lick=None, init=None, port_states=None):
        self.time = int(t)
        self.recording = int(rec)
        self.velocity = int(vel)
        self.absPosition = int(abs_pos)
        self.lap = int(lap)
        self.relPosition = int(rel_pos)
        self.lick = int(lick)
        self.initialized = int(init)
        self.portStates = map(int, port_states)

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
