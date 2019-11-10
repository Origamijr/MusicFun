from gui.window import Window
import wx

class MusicFunApp(wx.App):
    def OnInit(self):
        window = Window(title="MusicFun", size=(880, 480))
        window.Show()
        return True

if __name__ == '__main__':
    app = MusicFunApp()
    app.MainLoop()