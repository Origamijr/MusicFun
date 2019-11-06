from gui.window import Window
import wx

class MusicFunApp(wx.App):
    def OnInit(self):
        window = Window(None, title="MusicFun", size=(1280, 720))
        window.Show()
        return True

if __name__ == '__main__':
    app = MusicFunApp()
    app.MainLoop()