import wx
from wx import glcanvas
from OpenGL.GL import *
from gl.shader import initializeShaders, getShader
from gl.transform import Transform
import gl.glUtils as glUtils
import numpy as np
import glm

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
        self.Bind(wx.EVT_IDLE, self.OnIdle)

    def OnIdle(self, event):
        # Repaint on idle
        self.Refresh()

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
        glClearColor(0.1, 0.1, 0.15, 1.0)

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
        for node, shader_name, clear_depth_buffer in self.node_promise:
            # Add node directly
            if shader_name is not None:
                self.nodes.append((node.glNode(getShader(shader_name)), clear_depth_buffer))
            else:
                self.nodes.append((node.glNode(getShader(node.DEFAULT_SHADER)), clear_depth_buffer))
        

    def addNode(self, node, shader_name=None, clear_depth_buffer=False):
        """ Adds an object to be drawn. node must implement glNode """
        if self.init:
            # Add node directly
            if shader_name is not None:
                self.nodes.append((node.glNode(getShader(shader_name)), clear_depth_buffer))
            else:
                self.nodes.append((node.glNode(getShader(node.DEFAULT_SHADER)), clear_depth_buffer))
        else:
            # Add node to promise queue if not initialized
            self.node_promise.append((node, shader_name, clear_depth_buffer))

    def OnDraw(self):
        """ Draw "callback" """
        # Clear the screen to default color
        glClear(GL_COLOR_BUFFER_BIT)

        # Draw all nodes
        for node, clear_depth_buffer in self.nodes:
            if clear_depth_buffer: glClear(GL_DEPTH_BUFFER_BIT)
            node.draw(glm.mat4(1), self.cull_planes_window)

        # Swap the buffers
        self.SwapBuffers()