import pyo
import librosa
import numpy as np
import threading, time
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
        self.table_count = 3

        self.data = []
        self.np_emitter = NpBuffer(self.input, length=self.buf_size, overlap=self.overlap)
        self.trig = pyo.TrigFunc(self.np_emitter['trig'], self.get_data_rt)
        self.tables = self.table_count * [pyo.DataTable(self.buf_size)]
        self.faders = self.table_count * [pyo.Fader(fadein=overlap/sr, fadeout=overlap/sr, dur=buf_size/sr, mul=0.5)]
        self.oscs = [pyo.Osc(t, freq=self.sr / self.buf_size, mul=f) for t, f in zip(self.tables, self.faders)]
        # TODO add oscs
        self._base_objs = self.input.getBaseObjects()

    def get_data_rt(self):
        if self.playing:
            # skip if no data is available
            if self.np_emitter.np_buffer is None: return
            y = np.array(self.np_emitter.np_buffer)

            # Add the buffer to the data list
            self.data.append(y)

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

    def record(self):
        self.playing = True
        self.np_emitter.play()

    def stop_record(self):
        self.playing = False
        self.np_emitter.stop()

    def clear(self):
        self.data = []

    def play(self, seq=None):
        if seq is None: seq = [i for i in range(len(data))]
        duration = (self.buf_size - self.overlap) / self.sr
        print(duration)
        for osc in self.oscs: osc.out()

        for i, frame in enumerate(seq):
            thread = threading.Thread(target=self.play_table, args=(frame, i % self.table_count, i * duration))
            thread.start()

    def play_table(self, frame, player, delay):
        time.sleep(delay)
        self.tables[player].replace(list(self.data[frame]))
        self.oscs[player].out()
        self.faders[player].play()
