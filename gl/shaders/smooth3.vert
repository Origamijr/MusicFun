# version 330

in layout (location = 0) vec3 position;
in layout (location = 1) vec3 color;

uniform mat4 model = mat4(1);

out vec3 vertColor;

void main() {
    gl_Position = model * vec4(position, 1.0);
    vertColor = color;
}