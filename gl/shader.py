import sys
import os
from OpenGL.GL import *
#from OpenGL.GL.ARB.shader_objects import *
#from OpenGL.GL.ARB.fragment_shader import *
#from OpenGL.GL.ARB.vertex_shader import *

def loadSingleShader(filename, shaderType):
    shaderID = glCreateShader(shaderType)
    with open(filename, 'r') as file:
        code = file.read()
        glShaderSource(shaderID, code)
        glCompileShader(shaderID)
        infoLogLength = glGetShaderiv(shaderID, GL_INFO_LOG_LENGTH)
        if infoLogLength > 0:
            msg = "Error in %s: %s" % (filename, glGetShaderInfoLog(shaderID))
        else:
            msg = "Successfully compiled %s to id %d" % (filename, shaderID)
        print(msg)
        return shaderID

def loadShaders(vertID, fragID, name):
    programID = glCreateProgram()
    glAttachShader(programID, vertID)
    glAttachShader(programID, fragID)
    #glBindFragDataLocation(programID, 0, "fragColor")
    glLinkProgram(programID)

    linkStatus = glGetProgramiv(programID, GL_LINK_STATUS)
    if linkStatus != GL_TRUE:
        msg = "Shader Linking Error: %s" % (glGetShaderInfoLog(programID))
    else:
        msg = "Successfully Linked %s" % name
    print(msg)

    glDetachShader(programID, vertID)
    glDetachShader(programID, fragID)
    glDeleteShader(vertID)
    glDeleteShader(fragID)
    return programID

shaders = dict()

def initializeShaders():
    vertFiles = dict()
    fragFiles = dict()
    shaderPath = ""
    for path, dirs, files, in os.walk('.'):
        if "shaders" in dirs:
            shaderPath = os.path.join(path, "shaders")
    for filename in os.listdir(shaderPath):
        file = os.path.splitext(filename)
        filepath = os.path.join(shaderPath, filename)
        if file[1] == ".vert":
            vertFiles[file[0]] = loadSingleShader(filepath,  GL_VERTEX_SHADER)
        if file[1] == ".frag":
            fragFiles[file[0]] = loadSingleShader(filepath, GL_FRAGMENT_SHADER)
        if file[0] in vertFiles and file[0] in fragFiles and vertFiles[file[0]] != 0 and fragFiles[file[0]] != 0:
            shaders[file[0]] = loadShaders(vertFiles[file[0]], fragFiles[file[0]], file[0])

def getShader(shaderName):
    return shaders[shaderName]