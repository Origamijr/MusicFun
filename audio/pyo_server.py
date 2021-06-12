from pyo import *
from audio.config import SAMPLE_RATE
from audio.midi_synth import MidiSynth
from audio.audio_feature import AudioFeature
from audio.audio_segmenter import AudioSegmenter

s = Server(sr=SAMPLE_RATE, nchnls=2).boot().start()

mic = Input()

midi_synth = MidiSynth()
midi_synth.set("mul", 0.2)
midi_synth.start()

#f = AudioFeature(mic, mode='mel_spec', max_memory=1, t_resolution=1, update_time=0.05, n_resolution=256)
#f = AudioFeature(mic, mode='straight', max_memory=256, t_resolution=1024, update_time=0.05)
#f.play()

mic.out()

if __name__ == "__main__":
    import time

    s = Server().boot()
    s.start()
    t = CosTable([(0,0),(4095,1),(8192,0)])
    met = Metro(time=1, poly=3).play(delay=10)
    amp = TrigEnv(met, table=t, dur=.25, mul=.3)
    freq = TrigRand(met, min=400, max=400)
    a = Sine(freq=freq, mul=amp).out()

    s.gui(locals())