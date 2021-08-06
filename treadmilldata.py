
class TreadmillData:
    def __init__(self, t=0, rec=-1, vel=0, abs_pos=0, lap=0, rel_pos=0, lick=0, init=0, port_states=[0, 0, 0]):
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
