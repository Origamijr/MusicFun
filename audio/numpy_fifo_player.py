import pyo
import numpy as np
from queue import Queue
from functools import reduce
from audio.config import SAMPLE_RATE

class NpFIFOPlayer(pyo.PyoObject):
    """
    Pyo Object that stores numpy arrays in a FIFO and streams the output as audio
    """
    def __init__(self, input=None, buf_size=SAMPLE_RATE//4, overlap=0, patience=None, buffer_count=2, mul=1, add=0):
        """
        Parameters
        ----------
        input : PyoObject
            Parent PyoObject (stub)
        length : int
            Number of samples per buffer
        overlap : int
            Number of overlapping samples between adjacent buffers
        """
        pyo.PyoObject.__init__(self, mul, add)
        self.input = input
        self.buf_size = buf_size
        self.overlap = overlap
        self.patience = patience

        self.fifo = Queue()
        self.is_tfilling = True # filling tables (upon initial play)
        self.is_qfilling = False # filling queue (until patience reached)
        self.is_ready = False # ready to play
        self.is_playing = False # should be playing when ready

        # Tables and table readers do process grains of audio
        self.curr_buf = 0
        assert overlap <= buf_size / 2
        self.buffer_count = buffer_count
        if self.patience is None: self.patience = self.buffer_count
        self.tables = [pyo.DataTable(buf_size) for _ in range(self.buffer_count)]
        self.faders = [pyo.Fader(fadein=overlap/SAMPLE_RATE, fadeout=overlap/SAMPLE_RATE, dur=buf_size/SAMPLE_RATE, mul=mul) for _ in range(self.buffer_count)]
        self.oscs = [pyo.TableRead(t, freq=t.getRate(), mul=f) for t, f in zip(self.tables, self.faders)]
        self.sum = reduce(lambda a, b: a + b, self.oscs) + add
        
        # Timing mechanism to coordinate the tables
        self.p_metros = [pyo.Metro(time=(self.buffer_count * (buf_size - overlap) / SAMPLE_RATE)) for i in range(self.buffer_count)]
        self.p_trigs = [pyo.TrigFunc(m, self._play_table, arg=(i)) for i, m in enumerate(self.p_metros)]
        self.l_trigs = [pyo.TrigFunc(tbr['trig'], self._load_table, arg=(i)) for i, tbr in enumerate(self.oscs)]

        self._base_objs = self.sum.getBaseObjects()

    def _rotate_buf(self):
        ret = self.curr_buf
        self.curr_buf = (self.curr_buf + 1) % self.buffer_count
        return ret

    def put(self, buf):
        """
        Enqueues a numpy buffer into the FIFO
        """
        assert buf.shape == (self.buf_size,)
        if self.is_tfilling:
            self.tables[self.curr_buf].replace(list(buf))
            self._rotate_buf()
            if self.curr_buf == 0:
                self.is_tfilling = False
                self.is_qfilling = True
        elif self.is_qfilling and self.patience > 0:
            self.fifo.put(buf)
            if self.fifo.qsize() >= self.patience:
                self.is_qfilling = False
                if self.is_playing:
                    self._launch_metros()
                else:
                    self.is_ready = True
        elif self.is_qfilling and self.patience <= 0:
            self.fifo.put(buf)
            self.is_qfilling = False
            if self.is_playing:
                self._launch_metros()
            else:
                self.is_ready = True
        else:
            self.fifo.put(buf)

    def _load_table(self, ind):
        self.oscs[ind].stop()
        self.faders[ind].stop()
        if self.fifo.empty():
            self.fifo.put(np.zeros(self.buf_size))
        self.tables[ind].replace(list(self.fifo.get())) # Should this be threaded?

    def _play_table(self, ind):
        self.oscs[ind].play()
        self.faders[ind].play()

    def _launch_metros(self, delay=0):
        for i, m in enumerate(self.p_metros):
            m.play(delay=(delay+i*(self.buf_size-self.overlap)/SAMPLE_RATE))

    def play(self, dur=0, delay=0):
        self.is_playing = True
        if self.is_ready: self._launch_metros(delay=delay)
        return pyo.PyoObject.play(self, dur, delay)

    def out(self, chnl=0, inc=1, dur=0, delay=0):
        self.is_playing = True
        if self.is_ready: self._launch_metros(delay=delay)
        return pyo.PyoObject.out(self, chnl, inc, dur, delay)

    def stop(self, wait=0):
        self.is_tfilling = True
        self.is_qfilling = False
        self.is_ready = False
        self.is_playing = False
        self.curr_buf = 0
        for m in self.p_metros:
            m.stop(wait=wait)
        return pyo.PyoObject.stop(self, wait)