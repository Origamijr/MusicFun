import numpy as np

import glm

from OpenGL.GL import *

from gl.node import Node
from gl.shader import get_shader, is_ready

# TODO add comments

class Geometry(Node):

    def __init__(self, shader, filename=None, material=None, vertices=None, vertices2=None,
            colors=None, texCoords=None, normals=None, indices=None, 
            draw_mode=GL_TRIANGLES, line_width=1,
            **kwargs):
        super().__init__(**kwargs)
        
        # Acquire shader is promised
        if isinstance(shader, str):
            self.shader = get_shader(shader)
        else:
            self.shader = shader
            
        self.vao = glGenVertexArrays(1)
        self.draw_mode = draw_mode
        self.line_width = line_width
        self.material = material

        self.vertices = np.array(vertices, np.float32).reshape((-1, 3)) if vertices is not None else None
        self.vertices = np.array(vertices2, np.float32).reshape((-1, 2)) if vertices2 is not None else self.vertices
        self.colors = np.array(colors, np.float32).reshape((-1, 3)) if colors is not None else None
        self.texCoords = np.array(texCoords, np.float32).reshape((-1, 2)) if texCoords is not None else None
        self.normals = np.array(normals, np.float32).reshape((-1, 3)) if normals is not None else None
        self.indices = np.array(indices, np.int32).reshape((-1, 1)) if indices is not None else None
        
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
        self.uniforms = dict()


    def parse(self, filename):
        # TODO
        pass

    def setupVec3(self):
        # Bind VAO
        glBindVertexArray(self.vao)

        # Bind vertex data
        self.vbo = [glGenBuffers(1)]
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo[0])
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        posAttrib = glGetAttribLocation(self.shader, "position")
        glEnableVertexAttribArray(posAttrib)
        glVertexAttribPointer(posAttrib, 3, GL_FLOAT, GL_FALSE, 0, None)

        self.setup_rest(3)

    def setupVec2(self):
        # Bind VAO
        glBindVertexArray(self.vao)

        # Bind vertex data
        self.vbo = [glGenBuffers(1)]
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo[0])
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        posAttrib = glGetAttribLocation(self.shader, "position")
        glEnableVertexAttribArray(posAttrib)
        glVertexAttribPointer(posAttrib, 2, GL_FLOAT, GL_FALSE, 0, None)

        self.setup_rest(2)


    def setup_rest(self, dim):
        currVBO = 0

        # Bind color data
        posAttrib = glGetAttribLocation(self.shader, "color")
        if self.colors is not None and posAttrib >= 0:
                self.colors = self.matchLength(self.colors, self.vertices.size * 3 // dim)
                currVBO += 1
                self.vbo += [glGenBuffers(1)]
                glBindBuffer(GL_ARRAY_BUFFER, self.vbo[currVBO])
                glBufferData(GL_ARRAY_BUFFER, self.colors.nbytes, self.colors, GL_STATIC_DRAW)
                glEnableVertexAttribArray(posAttrib)
                glVertexAttribPointer(posAttrib, 3, GL_FLOAT, GL_FALSE, 0, None)

        # Bind indices
        if self.indices is None:
            self.indices = np.indices((1, self.vertices.size // dim))[1,0]
        currVBO += 1
        self.vbo += [glGenBuffers(1)]
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.vbo[currVBO])
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, GL_STATIC_DRAW)
        
        # Unbind buffers
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)


    def matchLength(self, a, length):
        """ Forces np array a to be the given length, using modulus for extension """
        if length > a.size:
            b = a
            while b.size + a.size < length:
                b = np.concatenate((b, a))
            return np.concatenate((b, a[:length-b.size]))
        else:
            return a[:length]

    def update_vertices(self, data, start=0):
        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo[0])
        glBufferSubData(GL_ARRAY_BUFFER, start, data.nbytes, data)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    def set_uniform(self, name, value, uniform_type):
        self.uniforms[name] = (value, uniform_type)




    def draw(self, C, cull_planes=None):
        # Set shader
        glUseProgram(self.shader)

        # Bind vertex array
        glBindVertexArray(self.vao)
        
        # Set uniforms
        modelLoc = glGetUniformLocation(self.shader, "model")
        if modelLoc >= 0:
            glUniformMatrix4fv(modelLoc, 1, GL_FALSE, glm.value_ptr(C))

        for name in self.uniforms:
            value, uniform_type = self.uniforms[name]
            loc = glGetUniformLocation(self.shader, name)
            if uniform_type == 'int':
                glUniform1i(loc, value)
            if uniform_type == 'float':
                glUniform1f(loc, value)
            if uniform_type == 'vec2':
                glUniform2f(loc, value[0], value[1])
            if uniform_type == 'vec3':
                glUniform3f(loc, value[0], value[1], value[2])
            if uniform_type == 'mat4':
                glUniformMatrix4fv(loc, 1, GL_FALSE, glm.value_ptr(value))
        
        # Other draw settings
        glLineWidth(self.line_width)

        # Draw geometry
        glDrawElements(self.draw_mode, self.indices.size, GL_UNSIGNED_INT, None)
        
        # Unbind vertex array
        glBindVertexArray(0)

    def update(self, C):
        pass