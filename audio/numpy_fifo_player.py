import pyo
from queue import Queue
from functools import reduce
from audio.config import SAMPLE_RATE

class NumpyFIFOPlayer(pyo.PyoObject):
    def __init__(self, input=None, buf_size=8192, overlap=0, patience=None):
        self.input = input
        self.buf_size = buf_size
        self.overlap = overlap
        self.patience = patience

        self.is_tfilling = True
        self.is_qfilling = False
        self.is_ready = False
        self.is_playing = False
        self.fifo = Queue()

        self.curr_buf = 0
        self.buffer_count = ((buf_size + 1) // (buf_size - overlap)) + 1
        if self.patience is None: self.patience = self.buffer_count
        self.tables = self.buffer_count * [pyo.DataTable(self.buf_size)]
        self.faders = self.buffer_count * [pyo.Fader(fadein=overlap/SAMPLE_RATE, fadeout=overlap/SAMPLE_RATE, dur=buf_size/SAMPLE_RATE, mul=0.5)]
        self.oscs = [pyo.Osc(t, freq=SAMPLE_RATE / self.buf_size, mul=f) for t, f in zip(self.tables, self.faders)]
        self.sum = reduce(lambda a, b: a + b, self.oscs)
        self._base_objs = self.sum.getBaseObjects()

    def _rotate_buf(self):
        self.curr_buf = (self.curr_buf + 1) % self.buffer_count

    def put(self, buf):
        assert buf.shape == (self.buf_size,)
        if self.is_tfilling:
            self.tables[self.curr_buf].replace(list(buf))
            self._rotate_buf()
            if self.curr_buf == 0:
                self.is_tfilling = False
                self.is_qfilling = True
        elif self.is_qfilling:
            self.fifo.put(buf)
            if self.fifo.qsize >= self.patience:
                self.is_qfilling = False
                self.is_ready = True
        else:
            self.fifo.put(buf)

    def play(self):
        self.is_playing = True
        return self

    