from gl.glUtils import translate
from gl.transform import Transform
import uuid

class MidiNote:
    def __init__(self, note, time, duration, velocity=64):
        self.note = note
        self.time = time
        self.duration = duration
        self.velocity = velocity
        self.id = uuid.uuid4()

    def __repr__(self):
        return '<midi_note note={} velocity={} duration={} time={}'.format(self.note, self.velocity, self.duration, self.time)