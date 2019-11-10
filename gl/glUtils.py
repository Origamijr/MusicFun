import glm

def translate(x, y, z=0):
    return glm.translate(glm.mat4(1), glm.vec3(x, y, z))

def scale(x, y=None, z=1):
    if y is None: return glm.scale(glm.mat4(1), glm.vec3(x, x, x))
    else: return glm.scale(glm.mat4(1), glm.vec3(x, y, z))

def rotate(angle, axis=(0, 0, 1)):
    return glm.rotate(glm.mat4(1), angle, glm.vec3(axis[0], axis[1], axis[2]))