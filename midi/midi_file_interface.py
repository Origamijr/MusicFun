import mido
from midi.midi_note_track import create_midi_note_track
from gl.transform import Transform

class MidiFileInterface():

    def __init__(self, filename):
        self.midifile = mido.MidiFile(filename)
        self.tracks = []
        for track in self.midifile.tracks:
            note_track = create_midi_note_track(track)
            if note_track is not None:
                self.tracks.append(note_track)

    def glNode(self, shader):
        root = Transform()
        colors = [(0, 0.3, 0.6), (0, 0.6, 0.3), (0.5, 0.2, 0.2)]
        for i, track in enumerate(self.tracks):
            root.addChild(track.glNode(shader, color=colors[i % len(colors)]))
        return root

    def print_tracks(self, meta_only=False):
        print(len(self.tracks))
        for track in self.tracks:
            track.print_notes()