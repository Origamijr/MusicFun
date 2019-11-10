import wx
from gui.opengl_canvas import OpenGLCanvas
from midi.midi_file_interface import MidiFileInterface
from gl.shader import getShader

class Window(wx.Frame):

    def __init__(self, title, size=(1280,720)):
        self.title = title
        self.size = size
        super(Window, self).__init__(None, title=self.title, size=self.size, 
            style=wx.DEFAULT_FRAME_STYLE | wx.FULL_REPAINT_ON_RESIZE)

        self.panel = Panel(self)


class Panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.SetBackgroundColour('#9999AA')

        self.canvas = OpenGLCanvas(self)
        self.midi_interface = MidiFileInterface('midi\samples\Sincerely - Violet Evergarden [Transcribed by UnknownEX1].mid')
        self.canvas.addNode(self.midi_interface, "flat2")

        self.play_midi_btn = wx.Button(self, label="Play", pos=(800, 10), size=(100, 50))
        self.play_midi_btn.SetBackgroundColour('#DDDDFF')
        self.Bind(wx.EVT_BUTTON, self.play_midi, self.play_midi_btn)
        self.midi_playing = False

    def play_midi(self, event):
        if self.midi_playing:
            self.midi_interface.stop()
        else:
            self.midi_interface.play()
        self.midi_playing = not self.midi_playing