from pyo import *

class MidiSynth:
    def __init__(self):
        self.mid = Notein()
        self.amp = MidiAdsr(self.mid['velocity'])
        self.pitch = MToF(self.mid['pitch'])
        self.osc = Osc(SquareTable(), freq=self.pitch, mul=self.amp).mix(1)
        self.rev = STRev(self.osc, revtime=1, cutoff=4000, bal=0.2).stop()

    def start(self):
        self.rev.out()

    def set(self, *args, **kwargs):
        self.rev.set(*args, **kwargs)

    def stop(self):
        self.rev.set('mul', 0, 1, self.tearoff)

    def tearoff(self):
        self.rev.stop()