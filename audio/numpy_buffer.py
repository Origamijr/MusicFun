import pyo
import numpy as np
from audio.config import SAMPLE_RATE
import threading

class NpBuffer(pyo.PyoObject):
    def __init__(self, input, length=882, buffer_count=2, overlap=0):
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
            self.ends.append(pyo.TrigFunc(table_rec['trig'], self.table_full))
        self._base_objs = self.data_ready.getBaseObjects()
        self._trig_objs = self._base_objs

    def table_full(self):
        if self.playing:
            #print(self.i)
            self.last_thread = threading.Thread(target=self.create_array, args=(self.curr_buf, self.last_thread))
            self.last_thread.start()
            self.curr_buf = 0 if self.curr_buf >= self.buffer_count - 1 else self.curr_buf + 1
            #print(self.i)
            self.rec_triggers[self.curr_buf].play()
        
    def create_array(self, curr_buf, last_thread):
        if last_thread is not None: last_thread.join()
        #print(" " + str(i) + " " + str(self.tables[i].get(0)))
        self.np_buffer = np.concatenate((self.overlap_buffer, np.asfarray(self.tables[curr_buf].getTable())))
        if self.overlap > 0: self.overlap_buffer = self.np_buffer[-self.overlap:]
        #print(self.np_buffer.shape)
        #print("triggerring")
        self.data_ready.play()

    def play(self, dur=0, delay=0):
        self.playing = True
        self.curr_buf = 0
        self.rec_triggers[self.curr_buf].play()
        #print(self.playing)
        return self

    def stop(self, wait=0):
        self.playing = False
        return self