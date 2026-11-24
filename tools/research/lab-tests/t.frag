#version 450
layout(set=0, binding=0) uniform U { vec4 off; } u;
layout(set=1, binding=0) uniform sampler2D tex;
layout(location=0) out vec4 o;
void main() { o = texture(tex, u.off.zw) + u.off; }
