import pyo
import numpy as np
from audio.config import SAMPLE_RATE
import threading

class NpBuffer(pyo.PyoObject):
    def __init__(self, input, length=882, buffer_count=2):
        duration = length / SAMPLE_RATE
        self.last_thread = None
        self.data_ready = pyo.Trig()
        self.rec_triggers = []
        self.tables = [] 
        self.ends = []
        self.buffer_count = buffer_count
        self.i = 0
        self.playing = False
        self.np_buffer = None
        for i in range(buffer_count):
            print(i)
            self.rec_triggers.append(pyo.Trig())
            self.tables.append(pyo.NewTable(duration))
            table_rec = pyo.TrigTableRec(input, self.rec_triggers[i], self.tables[i])
            self.ends.append(pyo.TrigFunc(table_rec['trig'], self.table_full))
        self._base_objs = self.data_ready.getBaseObjects()
        self._trig_objs = self._base_objs

    def table_full(self):
        if self.playing:
            #print(self.i)
            self.last_thread = threading.Thread(target=self.create_array, args=(self.i, self.last_thread))
            self.last_thread.start()
            self.i = 0 if self.i >= self.buffer_count - 1 else self.i + 1
            #print(self.i)
            self.rec_triggers[self.i].play()
        
    def create_array(self, i, last_thread):
        if last_thread is not None: last_thread.join()
        #print(" " + str(i) + " " + str(self.tables[i].get(0)))
        self.np_buffer = np.asfarray(self.tables[i].getTable())
        #print(i)
        self.data_ready.play()

    def play(self, dur=0, delay=0):
        self.playing = True
        self.i = 0
        self.rec_triggers[self.i].play()
        #print(self.playing)
        return self

    def stop(self, wait=0):
        self.playing = False
        return self