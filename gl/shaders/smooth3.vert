# version 330

layout (location = 0) in vec3 position;
layout (location = 1) in vec3 color;

uniform mat4 model = mat4(1);

out vec3 vertColor;

void main() {
    gl_Position = model * vec4(position, 1.0);
    vertColor = color;
}