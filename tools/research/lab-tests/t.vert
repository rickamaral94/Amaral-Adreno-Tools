#version 450
layout(set=0, binding=0) uniform U { vec4 off; } u;
void main() {
  vec2 p = vec2((gl_VertexIndex & 1) * 2.0 - 1.0, (gl_VertexIndex >> 1) * 2.0 - 1.0);
  gl_Position = vec4(p * 0.1 + u.off.xy, 0.0, 1.0);
}
