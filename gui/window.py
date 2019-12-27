import wx
from gui.opengl_canvas import OpenGLCanvas
from midi.midi_interface import MidiInterface
from audio.pyo_server import f

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
        #self.midi_interface = MidiInterface('midi\samples\Sincerely - Violet Evergarden [Transcribed by UnknownEX1].mid')
        self.midi_interface = MidiInterface('midi\samples\prokofiev.mid')
        #self.canvas.addNode(self.midi_interface)

        self.canvas.addNode(f)

        self.play_midi_btn = wx.Button(self, label="Play/Stop", pos=(700, 10), size=(100, 50))
        self.play_midi_btn.SetBackgroundColour('#DDDDFF')
        self.Bind(wx.EVT_BUTTON, self.play_midi, self.play_midi_btn)

    def play_midi(self, event):
        if self.midi_interface.playing:
            self.midi_interface.stop()
        else:
            self.midi_interface.play()