import wx
from wx import glcanvas
from OpenGL.GL import *
from gl.shader import initializeShaders, getShader
from gl.geode import Geode
import numpy as np

class OpenGLCanvas(glcanvas.GLCanvas):
    def __init__(self, parent):
        glcanvas.GLCanvas.__init__(self, parent, -1, size=(640, 480))

        self.init = False
        self.context = glcanvas.GLContext(self) 

        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self.Bind(wx.EVT_PAINT, self.OnPaint)


    def OnEraseBackground(self, event):
        pass # Do nothing, to avoid flashing on MSW.


    def OnPaint(self, event):
        """wx Paint callback"""
        dc = wx.PaintDC(self)
        self.SetCurrent(self.context)
        if not self.init:
            self.InitGL()
            self.init = True
        self.OnDraw()

    def InitGL(self):
        # Set clear color
        glClearColor(0.1, 0.15, 0.1, 1.0)

        # Initialize shaders
        initializeShaders()
        shaderProgram = getShader("flat2")
        glUseProgram(shaderProgram)

        vertices = [[0,0.5], [0.5,-0.5], [-0.5,-0.5]]
        color = [[1,0,0],[0,1,0],[0,0,1]]

        self.root = Geode(shaderProgram, vertices2=vertices, color=color)


    def OnDraw(self):
        #Clear the screen to black
        glClear(GL_COLOR_BUFFER_BIT)

        self.root.draw(np.identity(4))

        self.SwapBuffers()