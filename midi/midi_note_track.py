import uuid

from midi.midi_note import MidiNote
from midi.midi_interface import DEF_SECOND_SIZE
from mido.midifiles.tracks import _to_abstime
from mido.midifiles.units import tick2second
from gl.transform import Transform
from gl.geometry import Geometry
import gl.glUtils as glUtils

def create_midi_note_track(track, ticks_per_beat=48):
    for msg in track:
        if not msg.is_meta:
            return MidiNoteTrack(track, ticks_per_beat=ticks_per_beat)
    return None

class MidiNoteTrack:
    def __init__(self, track, ticks_per_beat=48):
        self.id = uuid.uuid4()
        self.ticks_per_beat = ticks_per_beat
        note_map = 128 * [None]
        self.notes = []
        self.tempos = []
        for msg in _to_abstime(track):
            #print(msg)
            if msg.type == 'note_on' and msg.velocity > 0:
                note_map[msg.note] = msg
            elif msg.type in ['note_on', 'note_off']:
                onset = note_map[msg.note]
                self.notes.append(MidiNote(msg.note, onset.time, msg.time - onset.time, onset.velocity))
            elif msg.type == 'set_tempo':
                self.tempos.append((msg.time, msg.tempo))
        self.notes.sort(key=lambda x: (x.time, x.note))

    def glNode(self, shader, color=(1, 1, 1)):
        # Create root node for track
        root = Transform(name="track{}".format(self.id))

        # Create geometry for individual notes
        vertices = [
            (0, 0),
            (1, 0),
            (0, 1),
            (1, 1)
        ]
        colors = [
            (color[0] - 0.1, color[1] - 0.1, color[2] - 0.1),
            (color[0] + 0.2, color[1] + 0.2, color[2] + 0.2)
        ]
        indices = [
            (0, 2, 1),
            (1, 2, 3)
        ]
        note_geometry = Geometry(shader, vertices2=vertices, colors=colors, indices=indices)

        # Setup iteration
        tempo = 500000
        curr_tempo = 0
        second_size = DEF_SECOND_SIZE
        
        last_tick = 0
        total_shift = 0

        chunk_counter = 0
        chunk_count = 1
        chunk_limit = 20
        chunk = Transform(name="chunk{}_{}".format(self.id, chunk_count))

        # iterate over notes
        for note in self.notes:

            while curr_tempo < len(self.tempos) and note.time >= self.tempos[curr_tempo][0]:
                # Update total shift amount before a new tempo is created
                total_shift += tick2second(self.tempos[curr_tempo][0] - last_tick, self.ticks_per_beat, tempo) * second_size
                last_tick = self.tempos[curr_tempo][0]
                
                # Update tempo
                tempo = self.tempos[curr_tempo][1]
                curr_tempo += 1
                
            # Update total shift amount
            total_shift += tick2second(note.time - last_tick, self.ticks_per_beat, tempo) * second_size
            last_tick = note.time

            # Calculate timescale
            timescale = tick2second(note.duration, self.ticks_per_beat, tempo) * second_size
            #print('shift:{} size:{} - time:{} duration:{}'.format(total_shift, timescale, note.time, note.duration))

            # Create note transform and parent the note geometry
            t = Transform(glUtils.translate(total_shift, note.note / 128) * glUtils.scale(timescale, 1 / 128), name="note{}".format(note.id))
            t.addChild(note_geometry)
            chunk.addChild(t)
            chunk_counter += 1

            # Break into chunks for better rendering performance
            if chunk_counter >= chunk_limit:
                root.addChild(chunk)
                chunk_count += 1
                chunk = Transform(name="chunk{}_{}".format(self.id, chunk_count))
                chunk_counter = 0

        if chunk_counter > 0: root.addChild(chunk)

        return root

    def print_notes(self):
        for note in self.notes:
            print(note)