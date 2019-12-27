from pyo import *
from audio.config import SAMPLE_RATE
from audio.midi_synth import MidiSynth
from audio.audio_feature import AudioFeature

s = Server(sr=SAMPLE_RATE).boot().start()

mic = Input()

midi_synth = MidiSynth()
midi_synth.set("mul", 0.2)
midi_synth.start()

f = AudioFeature(mic, mode='mel_spec', max_memory=1, t_resolution=1, update_time=0.05, n_resolution=256)
#f = AudioFeature(mic, mode='straight', max_memory=256, t_resolution=1024, update_time=0.05)
f.play()

#mic.out()

if __name__ == "__main__":
    s.gui(locals())