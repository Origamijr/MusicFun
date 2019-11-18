import pyo
import librosa
import numpy as np
from audio.config import SAMPLE_RATE
from audio.numpy_buffer import NpBuffer
from gl.geometry import Geometry
from gl.transform import Transform

class AudioFeature(pyo.PyoObject):
    def __init__(self, input, mode='straight', update_time=0.05, max_memory=1024):
        self.input = input
        self.mode = mode
        self.max_memory = max_memory
        self.data = np.ndarray((self.max_memory, 1))
        self.np_emitter = NpBuffer(self.input, length=1024)
        self.pat = pyo.Pattern(function=self.update_geometry, time=update_time)
        self.trig = pyo.TrigFunc(self.np_emitter['trig'], self.extract_feature_rt)
        self._base_objs = self.input.getBaseObjects()

    def extract_feature(self):
        if mode == 'straight':
            frames = self.np_emitter.np_buffer
        if mode == 'mel_spec':
            frames = librosa.feature.melspectrogram(y=self.np_emitter.np_buffer, sr=44100, hop_length=1024, n_mels=128)
        self.data[:-1,:] = self.data[1:,:]
        # TODO COMPLETE

    def update_geometry(self):
        pass
