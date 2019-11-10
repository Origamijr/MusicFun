from .midi_note import MidiNote
from mido.midifiles.tracks import _to_abstime
from gl.transform import Transform
from gl.geode import Geode
import gl.glUtils as glUtils
import uuid

def create_midi_note_track(track):
    for msg in track:
        if not msg.is_meta:
            return MidiNoteTrack(track)
    return None

class MidiNoteTrack:
    def __init__(self, track):
        self.id = uuid.uuid4()
        note_map = 128 * [None]
        self.notes = []
        for msg in _to_abstime(track):
            #print(msg.type)
            if msg.type == 'note_on' and msg.velocity > 0:
                note_map[msg.note] = msg
            elif msg.type in ['note_on', 'note_off']:
                onset = note_map[msg.note]
                self.notes.append(MidiNote(msg.note, onset.time, msg.time - onset.time, onset.velocity))
        self.notes.sort(key=lambda x: (x.time, x.note))

    def glNode(self, shader, color=(1, 1, 1)):
        root = Transform(name="track{}".format(self.id))

        vertices = [
            (0, 0),
            (1, 0),
            (0, 1),
            (1, 1)
        ]

        colors = [
            color,
            (color[0] + 0.1, color[1] + 0.1, color[2] + 0.1)
        ]

        indices = [
            (0, 2, 1),
            (1, 2, 3)
        ]

        g = Geode(shader, vertices2=vertices, colors=colors, indices=indices)

        timescale = 0.0001
        chunk_counter = 0
        chunk_count = 1
        chunk_limit = 20
        chunk = Transform(name="chunk{}_{}".format(self.id, chunk_count))
        for note in self.notes:
            t = Transform(glUtils.translate(note.time * timescale, note.note / 128) * glUtils.scale(note.duration * timescale, 1 / 128), name="note{}".format(note.id))
            t.addChild(g)
            chunk.addChild(t)
            chunk_counter += 1
            if chunk_counter >= chunk_limit:
                root.addChild(chunk)
                #print("time:{} center:{!r} radius:{} mat:{!r}".format(note.time, chunk.center, chunk.radius, chunk.M))
                chunk_count += 1
                chunk = Transform(name="chunk{}_{}".format(self.id, chunk_count))
                chunk_counter = 0
                chunk_count += 1
        if chunk_counter > 0: root.addChild(chunk)

        return root

    def print_notes(self):
        for note in self.notes:
            print(note)