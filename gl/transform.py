import glm
from .node import Node
import gl.glUtils as glUtils

class Transform(Node):
    def __init__(self, M=glm.mat4(1), **kwargs):
        super().__init__(**kwargs)
        self.M = M
        self.children = []
        self.min_x = self.min_y = self.min_z = self.max_x = self.max_y = self.max_z = None

    def applyMatrix(self, M):
        self.center = glm.vec3(M * glm.vec4(self.center, 1))
        self.radius = self.radius * glm.length(M * glm.vec4(1, 1, 1, 0)) / glm.sqrt(3)
        self.M = M * self.M

    def setMatrix(self, M):
        self.M = M
        centers = [self.M * glm.vec4(child.center, 1) for child in self.children]
        self.min_x = min([center[0] for center in centers])
        self.max_x = max([center[0] for center in centers])
        self.min_y = min([center[1] for center in centers])
        self.max_y = max([center[1] for center in centers])
        self.min_z = min([center[2] for center in centers])
        self.max_z = max([center[2] for center in centers])
        self.center = glm.vec3((self.min_x + self.max_x) / 2, (self.min_y + self.max_y) / 2, (self.min_z + self.max_z) / 2)
        self.radius = max([glm.length(self.center - child.center) + child.radius for child in self.children])

    def translate(self, x, y, z=0):
        self.applyMatrix(glUtils.translate(x, y, z))

    def addChild(self, child: Node):
        child_center = glm.vec3(self.M * glm.vec4(child.center, 1))
        child_radius = child.radius * glm.length(self.M * glm.vec4(1, 1, 1, 0)) / glm.sqrt(3)
        if len(self.children) == 0:
            self.center = child_center
            self.radius = child_radius
            self.min_x = self.max_x = self.center[0]
            self.min_y = self.max_y = self.center[1]
            self.min_z = self.max_z = self.center[2]
        else:
            self.min_x = min(self.min_x, child_center[0])
            self.max_x = max(self.max_x, child_center[0])
            self.min_y = min(self.min_y, child_center[1])
            self.max_y = max(self.max_y, child_center[1])
            self.min_z = min(self.min_z, child_center[2])
            self.max_z = max(self.max_z, child_center[2])
            new_center = glm.vec3((self.min_x + self.max_x) / 2, (self.min_y + self.max_y) / 2, (self.min_z + self.max_z) / 2)
            self.radius += glm.length(self.center - new_center)
            self.center = new_center
            self.radius = max(self.radius, glm.length(child_center - self.center) + child_radius)
            
        self.children.append(child)

    def remove_child(self, child):
        self.children.remove(child)
        child_center = glm.vec3(self.M * glm.vec4(child.center, 1))
        child_radius = child.radius * glm.length(self.M * glm.vec4(1, 1, 1, 0)) / glm.sqrt(3)
        if len(self.children) > 1:
            centers = [self.M * glm.vec4(child.center, 1) for child in self.children]
            self.min_x = min([center[0] for center in centers])
            self.max_x = max([center[0] for center in centers])
            self.min_y = min([center[1] for center in centers])
            self.max_y = max([center[1] for center in centers])
            self.min_z = min([center[2] for center in centers])
            self.max_z = max([center[2] for center in centers])
            self.center = glm.vec3((self.min_x + self.max_x) / 2, (self.min_y + self.max_y) / 2, (self.min_z + self.max_z) / 2)
            self.radius = max([glm.length(self.center - child.center) + child.radius for child in self.children])
            
        

    def draw(self, C, cull_planes=[]):
        if self.active:
            # pray that culling makes the program run better
            if not self.cull(C, cull_planes):
                T = C * self.M
                for child in self.children:
                    child.draw(T, cull_planes=cull_planes)

    def update(self, C):
        if self.active:
            T = C * self.M
            for child in self.children:
                child.update(T)