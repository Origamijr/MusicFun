import glm

class Node:
    def __init__(self, active=True, name="NA"):
        self.active = active
        self.center = glm.vec3(0)
        self.radius = 0
        self.name = name

    def setActive(self, active):
        self.active = active

    def cull(self, C, cull_planes):
        if len(cull_planes) > 0:
            center = glm.vec3(C * glm.vec4(self.center, 1))
            radius = self.radius * glm.length(C * glm.vec4(1, 1, 1, 0)) / glm.sqrt(3)
            for point, normal in cull_planes:
                dist = glm.dot(center - point, normal)
                if dist > radius:
                    #print('point:{!r} norm:{!r} dist:{} r:{}'.format(point, normal, dist, radius))
                    return True
            return False