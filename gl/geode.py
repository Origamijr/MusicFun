from OpenGL.GL import *
import numpy as np
from .node import Node
import glm

class Geode(Node):

    def __init__(self, shader, filename=None, material=None, vertices=None, vertices2=None,
            colors=None, texCoords=None, normals=None, indices=None, **kwargs):
        super().__init__(**kwargs)
        
        self.vao = glGenVertexArrays(1)
        self.shader = shader

        self.vertices = np.array(vertices, np.float32).reshape((-1, 3)) if vertices is not None else None
        self.vertices = np.array(vertices2, np.float32).reshape((-1, 2)) if vertices2 is not None else self.vertices
        self.colors = np.array(colors, np.float32).reshape((-1, 3)) if colors is not None else None
        self.texCoords = np.array(texCoords, np.float32).reshape((-1, 2)) if texCoords is not None else None
        self.normals = np.array(normals, np.float32).reshape((-1, 3)) if normals is not None else None
        self.indices = np.array(indices, np.int32).reshape((-1, 3)) if indices is not None else None
        
        self.material = material

        if filename is not None:
            self.parse(filename)
        elif vertices is not None:
            self.setupVec3()
        elif vertices2 is not None:
            self.setupVec2()
            
        min_x = np.min(self.vertices[:,0])
        max_x = np.max(self.vertices[:,0])
        min_y = np.min(self.vertices[:,1])
        max_y = np.max(self.vertices[:,1])
        min_z = np.min(self.vertices[:,2]) if vertices is not None else 0
        max_z = np.max(self.vertices[:,2]) if vertices is not None else 0
        self.center = glm.vec3((min_x + max_x) / 2, (min_y + max_y) / 2, (min_z + max_z) / 2)
        self.radius = glm.length(glm.vec3(max_x, max_y, max_z) - self.center)


    def parse(self, filename):
        pass

    def setupVec3(self):
        pass

    def setupVec2(self):

        glBindVertexArray(self.vao)
        currVBO = 0

        # Bind vertex data
        self.vbo = [glGenBuffers(1)]
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo[0])
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        posAttrib = glGetAttribLocation(self.shader, "position")
        glEnableVertexAttribArray(posAttrib)
        glVertexAttribPointer(posAttrib, 2, GL_FLOAT, GL_FALSE, 0, None)

        # Bind color data
        posAttrib = glGetAttribLocation(self.shader, "color")
        if self.colors is not None and posAttrib >= 0:
                self.colors = self.matchLength(self.colors, self.vertices.size * 3 // 2)
                currVBO += 1
                self.vbo += [glGenBuffers(1)]
                glBindBuffer(GL_ARRAY_BUFFER, self.vbo[currVBO])
                glBufferData(GL_ARRAY_BUFFER, self.colors.nbytes, self.colors, GL_STATIC_DRAW)
                glEnableVertexAttribArray(posAttrib)
                glVertexAttribPointer(posAttrib, 3, GL_FLOAT, GL_FALSE, 0, None)

        # Bind indices
        if self.indices is None:
            self.indices = np.indices((1, self.vertices.size // 2))[1,0]
        currVBO += 1
        self.vbo += [glGenBuffers(1)]
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.vbo[currVBO])
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, GL_STATIC_DRAW)
        
        # Unbind buffers
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)


    def matchLength(self, a, length):
        if length > a.size:
            b = a
            while b.size + a.size < length:
                b = np.concatenate((b, a))
            return np.concatenate((b, a[:length-b.size]))
        else:
            return a[:length]





    def draw(self, C, cull_planes=None):
        glUseProgram(self.shader)

        glBindVertexArray(self.vao)
        
        modelLoc = glGetUniformLocation(self.shader, "model")
        if modelLoc >= 0:
            glUniformMatrix4fv(modelLoc, 1, GL_FALSE, glm.value_ptr(C))
        
        glDrawElements(GL_TRIANGLES, self.indices.size, GL_UNSIGNED_INT, None)
        
        glBindVertexArray(0)

    def update(self, C):
        pass