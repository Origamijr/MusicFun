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

        self.node_promise = []
        self.nodes = []

        self.init = False
        self.context = glcanvas.GLContext(self)

        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnResize)


    def OnEraseBackground(self, event):
        pass # Do nothing, to avoid flashing on MSW.

    def OnPaint(self, event):
        """ Redraws scene when wx repaints """
        dc = wx.PaintDC(self)
        self.SetCurrent(self.context)
        if not self.init:
            self.InitGL()
            self.init = True
        self.OnDraw()

    def OnResize(self, event):
        """ Resizes viewport when canvas is resized """
        size = self.GetClientSize()
        glViewport(0, 0, size.width, size.height)

    def InitGL(self):
        """ Basic initialization """

        # Set clear color
        glClearColor(0.2, 0.1, 0.1, 1.0)

        # Enable blending for alphas
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Basic culling planes for 2d canvas
        self.cull_planes_window = [
            (glm.vec3(-1, -1, 0), glm.vec3(-1, 0, 0)),
            (glm.vec3(-1, -1, 0), glm.vec3(0, -1, 0)),
            (glm.vec3(1, 1, 0), glm.vec3(1, 0, 0)),
            (glm.vec3(1, 1, 0), glm.vec3(0, 1, 0))
        ]

        # Compile shaders
        initializeShaders()

        # Add promised nodes
        for node, shaderName in self.node_promise:
            self.nodes.append(node.glNode(getShader(shaderName)))
        

    def addNode(self, node, shaderName):
        """ Adds an object to be drawn. node must implement glNode """
        if self.init:
            # Add node directly
            self.nodes.append(node.glNode(getShader(shaderName)))
        else:
            # Add node to promise queue if not initialized
            self.node_promise.append((node, shaderName))

    def OnDraw(self):
        """ Draw "callback" """
        # Clear the screen to black
        glClear(GL_COLOR_BUFFER_BIT)

        # Draw all nodes
        for node in self.nodes:
            glClear(GL_DEPTH_BUFFER_BIT)
            node.draw(glm.mat4(1), self.cull_planes_window)

        # Swap the buffers
        self.SwapBuffers()