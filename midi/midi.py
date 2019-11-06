import mido

class Midi:

    def __init__(self, filename):
        self.mid = mido.MidiFile(filename)