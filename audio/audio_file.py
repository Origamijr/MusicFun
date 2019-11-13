import pyo

class AudioFile(pyo.PyoObject):
    def __init__(self, path):
        self.table = pyo.SndTable(path)