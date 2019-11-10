import mido
from midi.midi_note_track import create_midi_note_track
from gl.transform import Transform
from audio.pyo_server import s
import threading
import gl.glUtils as glUtils

class MidiFileInterface():

    def __init__(self, filename=None):
        self.midifile = mido.MidiFile(filename)
        self.tracks = []
        for track in self.midifile.tracks:
            note_track = create_midi_note_track(track)
            if note_track is not None:
                self.tracks.append(note_track)

    def play(self):
        """ Creates a thread that sends midi messages to be played """
        def play_task():
            t = threading.currentThread()
            for msg in self.midifile.play():
                print(msg)
                if getattr(t, "running", True):
                    s.addMidiEvent(*msg.bytes())
                else:
                    break
        self.play_thread = threading.Thread(target=play_task)
        self.play_thread.daemon = True
        self.play_thread.start()
    
    def stop(self):
        """ Stops the playing thread and turns off all midi notes """
        self.play_thread.running = False
        for i in range(128):
            s.addMidiEvent(*mido.Message('note_off', note=i).bytes())

    def glNode(self, shader):
        """ Generates a scene graph node to render """
        root = Transform(glUtils.translate(-1, -1) * glUtils.scale(1, 2))
        colors = [(0, 0.3, 0.6), (0, 0.6, 0.3), (0.5, 0.2, 0.2)]
        for i, track in enumerate(self.tracks):
            root.addChild(track.glNode(shader, color=colors[i % len(colors)]))
        return root

    def print_tracks(self, meta_only=False):
        """ Prints the notes in the track """
        print(len(self.tracks))
        for track in self.tracks:
            track.print_notes()