from pyo import *
from audio.config import SAMPLE_RATE
from audio.midi_synth import MidiSynth
from audio.audio_feature import AudioFeature
from audio.audio_segmenter import AudioSegmenter
from audio.audio_file import AudioFile
from audio.numpy_fifo_player import NpFIFOPlayer
from audio.audio_block_processor import AudioBlockProcessor

s = Server(sr=SAMPLE_RATE, nchnls=2).boot().start()

mic = Input()

#midi_synth = MidiSynth()
#midi_synth.set("mul", 0.2)
#midi_synth.start()

#f = AudioFeature(mic, mode='mel_spec', max_memory=1, t_resolution=1, update_time=0.05, n_resolution=256)
#f = AudioFeature(mic, mode='straight', max_memory=256, t_resolution=1024, update_time=0.05)
#f.play()


if __name__ == "__main__":
    af = AudioFile("C:/Users/origa/Desktop/python_stuff/MusicFun/audio/samples/Hype.wav")
    p = af.player.play()
    a = AudioBlockProcessor(p, buf_size=SAMPLE_RATE//16, overlap=100).out(chnl=0)

    #d = af.segment_data(buf_size=SAMPLE_RATE//8, overlap=100)
    #fp = NpFIFOPlayer(buf_size=SAMPLE_RATE//8, overlap=100)
    #for b in d: fp.put(b)
    #fp.out()
    s.gui(locals())