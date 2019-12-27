DEF_SECOND_SIZE = 0.2

import time
import threading

import mido
from mido.midifiles.tracks import _to_abstime, _to_reltime, merge_tracks
from mido.midifiles.units import tick2second

from OpenGL.GL import GL_LINES

from audio.pyo_server import s

from gl.node_object import NodeObject
from gl.transform import Transform
from gl.geometry import Geometry
import gl.gl_utils as gl_utils

from midi.midi_note_track import create_midi_note_track

class MidiInterface(NodeObject):
    """ Interface between mido and pyOpenGL """

    def __init__(self, filename=None, shader="flat2"):
        super().__init__(name="midi_interface")

        # Store the midifile
        self.midifile = mido.MidiFile(filename)

        # set state variables
        self.playing = False
        self.shader = shader

        # Extract meta messages and the corresponding track
        meta_track = []
        self.tempos = []
        for i, track in enumerate(self.midifile.tracks):
            for msg in _to_abstime(track):
                if msg.is_meta:
                    meta_track.append((msg, i))
                    if msg.type == 'set_tempo':
                        self.tempos.append(msg)
        meta_track.sort(key=lambda x: x[0].time)
        self.tempos.sort(key=lambda x: x.time)
        
        # Create the note tracks and add them to our list
        self.tracks = []
        for j, track in enumerate(self.midifile.tracks):
            # Merge in meta events not in track
            cut_meta_track = _to_reltime([msg for msg, i in meta_track if i != j])
            merged_track = merge_tracks([track, cut_meta_track])

            note_track = create_midi_note_track(merged_track, ticks_per_beat=self.midifile.ticks_per_beat)
            if note_track is not None:
                self.tracks.append(note_track)
                
    def gl_node_init(self):
        super().gl_node_init()
        self.track_t = Transform(gl_utils.translate(-1, -1) * gl_utils.scale(1, 2))
        colors = [(0, 0.3, 0.6), (0, 0.6, 0.3), (0.5, 0.2, 0.2)]
        for i, track in enumerate(self.tracks):
            self.track_t.add_child(track.gl_node(self.shader, color=colors[i % len(colors)]))
        self.track_t.add_child(self.generate_div_marks(self.shader, div=4))
        self.track_t.add_child(self.generate_playback_cursor(self.shader))
        self.gl_node_add_child(self.track_t)

    def play(self):
        """ Creates a thread that sends midi messages to be played """
        self.playing = True
        self.cursor_sync = None
        def _send_midi_task():
            t = threading.currentThread()
            elapsed_time = 0
            for msg in self.midifile.play(meta_messages=True):
                if getattr(t, "running", True):
                    if not msg.is_meta:
                        s.addMidiEvent(*msg.bytes())
                        elapsed_time += msg.time
                        self.cursor_sync = elapsed_time
                    elif msg.type == 'end_of_track':
                        self.stop()
                else:
                    break
            # Turn off all notes
            for i in range(128):
                s.addMidiEvent(*mido.Message('note_off', note=i).bytes())

        def _move_cursor_task():
            t = threading.currentThread()
            self.playback_cursor.setActive(True)
            last_time = time.perf_counter()
            total_distance = 0
            move_screen_count = 1
            while getattr(t, "running", True):
                # Sleep so there is a noticeable time difference
                time.sleep(0.05)

                # Evaluate distances
                curr_time = time.perf_counter()
                distance = (curr_time - last_time) * DEF_SECOND_SIZE
                last_time = curr_time

                # Quick hack to solve synchronization issues
                if self.cursor_sync is not None:
                    temp_distance = self.cursor_sync * DEF_SECOND_SIZE
                    distance += temp_distance - total_distance
                    total_distance = temp_distance
                    self.cursor_sync = None
                else:
                    total_distance += distance
                self.playback_cursor.set_matrix(gl_utils.translate(total_distance, 0))

                # Scroll screen if cursor is near end
                if total_distance > 1.8 * move_screen_count:
                    self.track_t.translate(-1.8, 0)
                    move_screen_count += 1

            self.playback_cursor.setActive(False)
            self.track_t.set_matrix(gl_utils.translate(-1, -1) * gl_utils.scale(1, 2))

        self.send_midi_thread = threading.Thread(target=_send_midi_task)
        self.send_midi_thread.daemon = True
        self.send_midi_thread.start()

        self.move_cursor_thread = threading.Thread(target=_move_cursor_task)
        self.move_cursor_thread.daemon = True
        self.move_cursor_thread.start()
    
    def stop(self):
        """ Stops all playing threads """
        self.send_midi_thread.running = False
        self.move_cursor_thread.running = False
        self.playing = False

    def generate_div_marks(self, shader, div=4):
        """ Creates those grey bars to denote a pulse """
        # Create root for divisions
        root = Transform(name="divs")

        # Create geometry for beat division
        vertices = [
            (0, 0),
            (0, 1)
        ]
        color = (0.2, 0.2, 0.2)
        div_geometry = Geometry(shader, vertices2=vertices, colors=color, draw_mode=GL_LINES)

        # Set up iteration
        tempo = 500000
        curr_tempo = 0
        second_size = DEF_SECOND_SIZE
        
        last_tick = 0
        total_shift = 0

        chunk_counter = 0
        chunk_count = 1
        chunk_limit = 20
        chunk = Transform(name="div_chunk_{}".format(chunk_count))

        curr_div = 0
        final_shift = self.midifile.length + (2 / second_size)
        while total_shift / second_size < final_shift:
            curr_tick = curr_div * self.midifile.ticks_per_beat * 4 / div

            while curr_tempo < len(self.tempos) and curr_tick >= self.tempos[curr_tempo].time:
                # Update total shift amount before a new tempo is created
                total_shift += tick2second(self.tempos[curr_tempo].time - last_tick, self.midifile.ticks_per_beat, tempo) * second_size
                last_tick = self.tempos[curr_tempo].time
                
                # Update tempo
                tempo = self.tempos[curr_tempo].tempo
                curr_tempo += 1
                
            # Update total shift amount
            total_shift += tick2second(curr_tick - last_tick, self.midifile.ticks_per_beat, tempo) * second_size
            last_tick = curr_tick

            # Create transform and parent the note geometry
            t = Transform(gl_utils.translate(total_shift, 0), name="div_{}".format(curr_div))
            t.add_child(div_geometry)
            chunk.add_child(t)
            chunk_counter += 1

            # Break into chunks for better rendering performance
            if chunk_counter >= chunk_limit:
                root.add_child(chunk)
                chunk_count += 1
                chunk = Transform(name="div_chunk_{}".format(chunk_count))
                chunk_counter = 0
            
            curr_div += 1

        if chunk_counter > 0: root.add_child(chunk)

        return root

    def generate_playback_cursor(self, shader):
        """ Create that thing that moves when the song is played """
        self.playback_cursor = Transform(name="cursor")
        
        # Create geometry
        vertices = [
            (0, 0),
            (0, 1)
        ]
        color = (0.8, 0.8, 0.2)
        cursor_geometry = Geometry(shader, vertices2=vertices, colors=color, draw_mode=GL_LINES, line_width=2)
        self.playback_cursor.add_child(cursor_geometry)
        self.playback_cursor.setActive(False)

        return self.playback_cursor

    def print_tracks(self, meta_only=False):
        """ Prints the notes in the track """
        print(len(self.tracks))
        for track in self.tracks:
            track.print_notes()