from OpenGL.GL import *
import numpy as np

class Geode:

    def __init__(self, shader, filename=None, material=None, vertices=None, vertices2=None,
            color=None, texCoords=None, normals=None, indices=None):
        
        self.vao = glGenVertexArrays(1)
        self.shader = shader

        self.vertices = np.array(vertices, np.float32).flatten() if vertices is not None else None
        self.vertices2 = np.array(vertices2, np.float32).flatten() if vertices2 is not None else None
        self.color = np.array(color, np.float32).flatten() if color is not None else None
        self.texCoords = np.array(texCoords, np.float32).flatten() if texCoords is not None else None
        self.normals = np.array(normals, np.float32).flatten() if normals is not None else None
        self.indices = np.array(indices, np.int32).flatten() if indices is not None else None
        
        self.material = material

        if filename is not None:
            self.parse(filename)
        elif vertices is not None:
            self.setupVec3()
        elif vertices2 is not None:
            self.setupVec2()

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
        glBufferData(GL_ARRAY_BUFFER, self.vertices2.nbytes, self.vertices2, GL_STATIC_DRAW)
        posAttrib = glGetAttribLocation(self.shader, "position")
        glEnableVertexAttribArray(posAttrib)
        glVertexAttribPointer(posAttrib, 2, GL_FLOAT, GL_FALSE, 0, None)

        # Bind color data
        posAttrib = glGetAttribLocation(self.shader, "color")
        if self.color is not None and posAttrib >= 0:
                self.color = self.matchLength(self.color, self.vertices2.size * 3 // 2)
                currVBO += 1
                self.vbo += [glGenBuffers(1)]
                glBindBuffer(GL_ARRAY_BUFFER, self.vbo[currVBO])
                glBufferData(GL_ARRAY_BUFFER, self.color.nbytes, self.color, GL_STATIC_DRAW)
                glEnableVertexAttribArray(posAttrib)
                glVertexAttribPointer(posAttrib, 3, GL_FLOAT, GL_FALSE, 0, None)

        # Bind indices
        if self.indices is None:
            self.indices = np.indices((1, self.vertices2.size // 2))[1,0]
        currVBO += 1
        self.vbo += [glGenBuffers(1)]
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.vbo[currVBO])
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, GL_STATIC_DRAW)
        
        # Unbind buffers
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)


    def matchLength(self, b, length):
        if length > b.size:
            c = b
            while c.size + b.size < length:
                c = np.concatenate((c, b))
            return np.concatenate((c, b[:length-c.size]))
        else:
            return b[:length]


    def draw(self, C):
        glUseProgram(self.shader)

        glBindVertexArray(self.vao)
        
        modelLoc = glGetUniformLocation(self.shader, "model")
        if modelLoc >= 0:
            glUniformMatrix4fv(modelLoc, 1, GL_FALSE, C)
        
        glDrawElements(GL_TRIANGLES, self.indices.size, GL_UNSIGNED_INT, None)
        
        glBindVertexArray(0)