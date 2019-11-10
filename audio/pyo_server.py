from pyo import *

s = Server().boot().start()

# A little audio synth to play the MIDI events.
mid = Notein()
amp = MidiAdsr(mid['velocity'])
pit = MToF(mid['pitch'])
osc = Osc(SquareTable(), freq=pit, mul=amp).mix(1)
rev = STRev(osc, revtime=1, cutoff=4000, bal=0.2).out()