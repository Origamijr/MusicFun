import pyo
import librosa
import numpy as np
import threading
from OpenGL.GL import GL_LINE_STRIP, GL_TRIANGLES, glGenVertexArrays

from audio.config import SAMPLE_RATE
from audio.numpy_buffer import NpBuffer

from gl.geometry import Geometry
from gl.transform import Transform
from gl.node_object import NodeObject
from gl.gl_utils import gl_ready, translate, scale, rotate

class AudioSegmenter(pyo.PyoObject):
    def __init__(self, input, buf_size=8192, overlap=1024, sr=44100):
        self.input = input
        self.overlap = overlap
        self.buf_size = buf_size
        self.sr = sr

        self.data = []
        self.np_emitter = NpBuffer(self.input, length=self.buf_size, overlap=self.overlap)
        self.trig = pyo.TrigFunc(self.np_emitter['trig'], self.get_data_rt)
        self._base_objs = self.input.getBaseObjects()

    def get_data_rt(self):
        if self.playing:
            # skip if no data is available
            if self.np_emitter.np_buffer is None: return
            y = np.array(self.np_emitter.np_buffer)

            # Add the buffer to the data list
            data.append(y)

    def get_slice(self, time, duration):
        frame = (int)(time * self.sr) / self.buf_size
        frame_samp = (int)(time * self.sr) % self.buf_size
        tot_samps = (int)(duration * self.sr)
        a = np.zeros(tot_samps)
        while tot_samps > 0:
            copy_size = min(self.buf_size - frame_samp, tot_samps)
            a[-tot_samps:-tot_samps + copy_size] = self.data[frame][frame_samp:copy_size]
            frame_samp = 0
        return a

    def play(self):
        self.playing = True
        self.np_emitter.play()

    def stop(self):
        self.playing = False
        self.np_emitter.stop()

    def clear(self):
        self.data = []
