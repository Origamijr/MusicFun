from pyo import *
from audio.config import SAMPLE_RATE
from audio.midi_synth import MidiSynth

s = Server(sr=SAMPLE_RATE).boot().start()

#mic = Input()

midi_synth = MidiSynth()
midi_synth.set("mul", 0.2)
midi_synth.start()

#mic.out()

if __name__ == "__main__":
    s.gui(locals())