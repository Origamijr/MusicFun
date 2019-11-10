import glm
import uuid

class Node:
    def __init__(self, active=True, name="NA"):
        self.active = active
        self.center = glm.vec3(0)
        self.radius = 0
        self.name = name
        self.id = uuid.uuid4()

    def __eq__(self, other):
        if isinstance(other, Node):
            return self.id == other.id
        return NotImplemented

    def setActive(self, active):
        self.active = active

    def cull(self, C, cull_planes):
        if len(cull_planes) > 0:
            center = glm.vec3(C * glm.vec4(self.center, 1))
            radius = self.radius * glm.length(C * glm.vec4(1, 1, 1, 0)) / glm.sqrt(3)
            for point, normal in cull_planes:
                dist = glm.dot(center - point, normal)
                if dist > radius:
                    if self.name == "cursor":
                        print('name:{} point:{!r} norm:{!r} dist:{} r:{} center:{!r} prev_center:{!r}'.format(self.name, point, normal, dist, radius, center, self.center))
                    return True
            return False