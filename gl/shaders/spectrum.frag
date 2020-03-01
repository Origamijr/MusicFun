# version 330

in vec3 vertColor;
in vec3 fragPos;

out vec4 fragColor;

void main() {
    //vertColor = vec3(0.0f,1.0f,0.5f);
    fragColor = vec4(min(0.1 + sqrt(abs(fragPos.y)), 1) * vertColor, 1);
    fragColor = vec4(min(0.1 + sqrt(abs(fragPos.y)), 1) * vec3(0.0f,1.0f,0.5f), 1);
}