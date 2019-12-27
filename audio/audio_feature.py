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

class AudioFeature(pyo.PyoObject, NodeObject):
    def __init__(self, input, mode='straight', update_time=0.1, max_memory=8192, t_resolution=-1, buf_size=8192, overlap=-1, n_resolution=-1):
        super().__init__()
        self.gl_node_manual_init("audio_feature")
        self.gl_node_set_idle_callback(self.update_geometry, update_time)

        self.input = input
        self.mode = mode
        self.max_memory = max_memory
        self.t_resolution = t_resolution
        self.n_resolution = n_resolution
        self.buf_size = buf_size
        self.resolution_warning = False
        self.overlap = overlap
        self.playing = False
        self.last_thread = None
        self.root = Transform(name="audio_feature_root")
        self.geometry = None

        if self.mode == 'straight':
            if self.t_resolution < 1: self.t_resolution = self.buf_size
            if self.overlap < 0: self.overlap = 0
        elif self.mode == 'mel_spec':
            if self.n_resolution < 1: self.n_resolution = 128
            if self.t_resolution < 1: self.t_resolution = 8
            self.hop_length = self.buf_size // self.t_resolution
            if self.overlap < 0: self.overlap = self.hop_length // 2
            self.n_fft = self.hop_length + self.overlap
        else:
            print("invalid feature mode >:(")

        self.data = None
        self.np_emitter = NpBuffer(self.input, length=self.buf_size, overlap=self.overlap)
        #self.pat = pyo.Pattern(function=self.update_geometry, time=update_time)
        self.trig = pyo.TrigFunc(self.np_emitter['trig'], self.extract_feature_rt)
        self._base_objs = self.input.getBaseObjects()

    def extract_feature_rt(self):
        if self.playing:
            # skip if no data is available
            if self.np_emitter.np_buffer is None: return
            y = np.array(self.np_emitter.np_buffer)

            self.last_thread = threading.Thread(target=self._extract_feature_thread, args=(y, self.last_thread))
            self.last_thread.start()
        

    def _extract_feature_thread(self, y, last_thread):
        # Get frame data
        if self.mode == 'straight':
            frames = np.reshape(y, (-1,1))
        elif self.mode == 'mel_spec':
            y = np.pad(y, (0, self.n_fft - self.hop_length), mode='reflect')
            frames = librosa.feature.melspectrogram(y=y, sr=44100, n_fft=self.n_fft, hop_length=self.hop_length, n_mels=self.n_resolution, center=False).T
            #frames = librosa.power_to_db(S=frames, ref=0.1)
        else:
            print("invalid feature mode >:(")

        if last_thread is not None: last_thread.join()

        # Adjust instance variables if necessary
        if not self.resolution_warning and frames.shape[0] > self.t_resolution and frames.shape[0] % self.t_resolution != 0:
            print("Warning: t_resolution %d does not divide frame count %d. Possibly uneven frame durations" % (self.t_resolution, frames.shape[0]))
            self.resolution_warning = True
        
        # Set up data if first iteration
        if self.data is None:
            self.data = np.ndarray((self.max_memory, frames.shape[1], 3), dtype=np.float32)
            self.data[:,:,0] = np.linspace(0.0, 1.0, num=self.max_memory, dtype=np.float32).reshape((self.max_memory, 1)).repeat(frames.shape[1], axis=1)
            self.data[:,:,2] = np.linspace(0.0, 1.0, num=frames.shape[1], dtype=np.float32).reshape((1, frames.shape[1])).repeat(self.max_memory, axis=0)
            
        # Rotate and copy the data
        copy_size = min(self.t_resolution, self.data.shape[0])
        jump = max(1, frames.shape[0] // self.t_resolution)
        self.data[:-copy_size,:,1] = self.data[copy_size:,:,1]
        self.data[-copy_size:,:,1] = frames[:copy_size * jump:jump,:]

    def update_geometry(self):
        if self.data is not None and self.geometry is not None:
            #print("%r %r" % (self.data.nbytes, self.indices.shape))
            self.geometry.update_vertices(self.data)
        

    def gl_node_init(self):
        super().gl_node_init()

        if self.data.shape[0] == 1 or self.data.shape[1] == 1:
            mode = GL_LINE_STRIP
            self.indices = [i for i in range(max(self.data.shape[0], self.data.shape[1]))]
        else:
            mode = GL_TRIANGLES
            self.indices = []
            T = self.data.shape[0]
            N = self.data.shape[1]
            for t in range(T - 1):
                for i in range(N - 1):
                    self.indices.append((T * t + i, T * t + (i + 1), T * (t + 1) + (i + 1)))
                    self.indices.append((T * t + i, T * (t + 1) + (i + 1), T * (t + 1) + i))
        self.geometry = Geometry("spectrum", vertices=self.data, indices=self.indices, colors=((0,1,1)), draw_mode=mode, line_width=3)
        if mode == GL_LINE_STRIP:
            if self.data.shape[0] > self.data.shape[1]:
                m = translate(-1, 0) * scale(2)
            else:
                m = translate(-1, -0.5) * rotate(1.57, (0,1,0)) *  scale(1, 0.01, 2)
        else:
            m = translate(-1, 1, -1) * rotate(1.57, (1,0,0)) * scale(2)
        t = Transform(M=m, name="audio_feature_normalize")
        #print(t.M)
        t.add_child(self.geometry)

        self.gl_node_add_child(t)
        return self.root

    def play(self):
        self.playing = True
        self.np_emitter.play()

    def stop(self):
        self.playing = False
        self.np_emitter.stop()
