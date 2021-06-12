import pyo
import numpy as np
from audio.config import SAMPLE_RATE
import threading

class NpBuffer(pyo.PyoObject): 
    """
    Pyo Object that stores streamed input into overlapping numpy arrays
    ...
    Usage
    -----
    NpBuffers trigger a pyo trigger everytime a buffer is filled
        pyo.TrigFunc(self.np_buffer['trig'], callback)

    Extract data in callback
        if self.np_emitter.np_buffer is None: return
        y = np.array(self.np_emitter.np_buffer)
    """

    def __init__(self, input, length=882, buffer_count=2, overlap=0):
        """
        Parameters
        ----------
        input : PyoObject
            Parent PyoObject
        length : int
            Number of samples per buffer
        buffer_count : int 
            Number of buffers used to record (min 2)
        overlap : int
            Number of overlapping samples between adjacent buffers
        """

        duration = (length - overlap) / SAMPLE_RATE
        self.last_thread = None
        self.data_ready = pyo.Trig()
        self.rec_triggers = []
        self.tables = [] 
        self.ends = []
        self.overlap = overlap
        self.overlap_buffer = np.zeros(self.overlap)
        self.buffer_count = buffer_count
        self.curr_buf = 0
        self.playing = False
        self.np_buffer = None
        
        for i in range(buffer_count):
            self.rec_triggers.append(pyo.Trig())
            self.tables.append(pyo.NewTable(duration))
            table_rec = pyo.TrigTableRec(input, self.rec_triggers[i], self.tables[i])
            self.ends.append(pyo.TrigFunc(table_rec['trig'], self._table_full))

        self._base_objs = self.data_ready.getBaseObjects()
        self._trig_objs = self._base_objs

    def _table_full(self):
        """
        Callback to be called when table being recorded into is full
        """
        if self.playing:
            self.last_thread = threading.Thread(target=self._create_array, args=(self.curr_buf, self.last_thread))
            self.last_thread.start()
            self.curr_buf = 0 if self.curr_buf >= self.buffer_count - 1 else self.curr_buf + 1
            self.rec_triggers[self.curr_buf].play()
        
    def _create_array(self, curr_buf, last_thread):
        """
        Callback to read data recorded into a table into a numpy array
        """
        if last_thread is not None: last_thread.join()
        self.np_buffer = np.concatenate((self.overlap_buffer, np.asfarray(self.tables[curr_buf].getTable())))
        if self.overlap > 0: self.overlap_buffer = self.np_buffer[-self.overlap:]
        self.data_ready.play()

    def play(self, dur=0, delay=0):
        self.playing = True
        self.curr_buf = 0
        self.rec_triggers[self.curr_buf].play()
        return self

    def stop(self, wait=0):
        self.playing = False
        return self