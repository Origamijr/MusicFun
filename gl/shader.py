import sys
import os
from OpenGL.GL import *

shaders = dict()
initialized = False

def load_single_shader(filename, shaderType):
    shaderID = glCreateShader(shaderType)
    with open(filename, 'r') as file:
        code = file.read()
        glShaderSource(shaderID, code)
        glCompileShader(shaderID)
        infoLogLength = glGetShaderiv(shaderID, GL_INFO_LOG_LENGTH)
        if infoLogLength > 0:
            print("Error in %s: %s" % (filename, glGetShaderInfoLog(shaderID)))
        return shaderID

def load_shaders(vertID, fragID, name):
    programID = glCreateProgram()
    glAttachShader(programID, vertID)
    glAttachShader(programID, fragID)
    #glBindFragDataLocation(programID, 0, "fragColor")
    glLinkProgram(programID)

    linkStatus = glGetProgramiv(programID, GL_LINK_STATUS)
    if linkStatus != GL_TRUE:
        print("Shader Linking Error: %s" % (glGetShaderInfoLog(programID)))

    glDetachShader(programID, vertID)
    glDetachShader(programID, fragID)
    glDeleteShader(vertID)
    glDeleteShader(fragID)
    return programID

def initialize_shaders():
    """ Compiles all shaders in the "shaders" folder. Must be called after context is created """
    global initialized
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
            vertFiles[file[0]] = load_single_shader(filepath,  GL_VERTEX_SHADER)
        if file[1] == ".frag":
            fragFiles[file[0]] = load_single_shader(filepath, GL_FRAGMENT_SHADER)
        if file[0] in vertFiles and file[0] in fragFiles and vertFiles[file[0]] != 0 and fragFiles[file[0]] != 0:
            shaders[file[0]] = load_shaders(vertFiles[file[0]], fragFiles[file[0]], file[0])
    initialized = True

def is_ready():
    return initialized

def get_shader(shader_name):
    """ Get a shader ID for the given file name """
    return shaders[shader_name]