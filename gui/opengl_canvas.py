import wx
from wx import glcanvas
from OpenGL.GL import *
from gl.shader import initializeShaders, getShader
from gl.transform import Transform
import gl.glUtils as glUtils
import numpy as np
import glm
from midi.midi_file_interface import MidiFileInterface

class OpenGLCanvas(glcanvas.GLCanvas):
    def __init__(self, parent):
        glcanvas.GLCanvas.__init__(self, parent, -1, size=(640, 480))

        self.init = False
        self.context = glcanvas.GLContext(self) 

        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnResize)


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

    def OnResize(self, event):
        size = self.GetClientSize()
        glViewport(0, 0, size.width, size.height)

    def InitGL(self):
        # Set clear color
        glClearColor(0.1, 0.15, 0.1, 1.0)

        # Initialize shaders
        initializeShaders()
        shaderProgram = getShader("flat2")

        self.cull_planes_window = [
            (glm.vec3(-1, -1, 0), glm.vec3(-1, 0, 0)),
            (glm.vec3(-1, -1, 0), glm.vec3(0, -1, 0)),
            (glm.vec3(1, 1, 0), glm.vec3(1, 0, 0)),
            (glm.vec3(1, 1, 0), glm.vec3(0, 1, 0))
        ]

        #vertices = [[0,0.5], [0.5,-0.5], [-0.5,-0.5]]
        #color = [[1,0,0],[0,1,0],[0,0,1]]

        #self.root = Geode(shaderProgram, vertices2=vertices, colors=color)

        midi = MidiFileInterface('midi/samples/prokofiev.mid')
        midi_node = midi.glNode(shaderProgram)
        
        self.root = Transform(glUtils.translate(-1, -1) * glUtils.scale(1, 2))
        self.root.addChild(midi_node)


    def OnDraw(self):
        #Clear the screen to black
        glClear(GL_COLOR_BUFFER_BIT)

        self.root.draw(glm.mat4(1), self.cull_planes_window)

        self.SwapBuffers()