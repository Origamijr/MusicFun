from gui.window import Window
import wx
from midi.midi_file_interface import MidiFileInterface

class MusicFunApp(wx.App):
    def OnInit(self):
        window = Window(title="MusicFun", size=(960, 640))
        window.Show()
        return True

if __name__ == '__main__':
    app = MusicFunApp()
    app.MainLoop()