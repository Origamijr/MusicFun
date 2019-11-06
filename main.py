from gui.window import Window
import wx

def main():
    app = wx.App()

    window = Window(None, title="MusicFun")
    window.Show()

    app.MainLoop()

if __name__ == '__main__':
    main()