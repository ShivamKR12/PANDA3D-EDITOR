#version 150

// This is the terrain fragment shader. There is a lot of code in here
// which is not necessary to render the terrain, but included for convenience -
// Like generating normals from the heightmap or a simple fog effect.

// Most of the time you want to adjust this shader to get your terrain the look
// you want. The vertex shader most likely will stay the same.

in vec2 terrain_uv;
in vec3 vtx_pos;
out vec4 color;

uniform struct {
  sampler2D data_texture;
  sampler2D heightfield;
  int view_index;
  int terrain_size;
  int chunk_size;
} ShaderTerrainMesh;

uniform sampler2D p3d_Texture0;
uniform vec3 wspos_camera;

// Brush uniforms
uniform vec4 brush_pos;
uniform float brush_size;

// Compute normal from the heightmap, this assumes the terrain is facing z-up
vec3 get_terrain_normal() {
  const float terrain_height = 50.0;
  vec3 pixel_size = vec3(1.0, -1.0, 0) / textureSize(ShaderTerrainMesh.heightfield, 0).xxx;
  float u0 = texture(ShaderTerrainMesh.heightfield, terrain_uv + pixel_size.yz).x * terrain_height;
  float u1 = texture(ShaderTerrainMesh.heightfield, terrain_uv + pixel_size.xz).x * terrain_height;
  float v0 = texture(ShaderTerrainMesh.heightfield, terrain_uv + pixel_size.zy).x * terrain_height;
  float v1 = texture(ShaderTerrainMesh.heightfield, terrain_uv + pixel_size.zx).x * terrain_height;
  vec3 tangent = normalize(vec3(1.0, 0, u1 - u0));
  vec3 binormal = normalize(vec3(0, 1.0, v1 - v0));
  return normalize(cross(tangent, binormal));
}

void main() {
  vec3 diffuse = texture(p3d_Texture0, terrain_uv * 16.0).xyz;
  vec3 normal = get_terrain_normal();

  // Add some fake lighting - you usually want to use your own lighting code here
  vec3 fake_sun = normalize(vec3(0.8549, 0.8549, 0.8549));
  vec3 shading = max(0.0, dot(normal, fake_sun)) * diffuse;
  shading += vec3(0.1216, 0.1216, 0.1216);

  // Fake fog
  float dist = (distance(vtx_pos, wspos_camera) / 2.0);
  float fog_factor = smoothstep(0, 1, dist / 1000.0);
<<<<<<< Updated upstream
  shading = mix(shading, vec3(0.8078, 0.8078, 0.8078), fog_factor);
=======
  shading = mix(shading, vec3(0.8275, 0.8275, 0.8275), fog_factor);
>>>>>>> Stashed changes

  vec4 terrainColor = vec4(shading, 1.0);

  // Calculate brush influence
  vec2 brush_uv = ((vtx_pos.xy - brush_pos.xy) / brush_size + 0.5);
  float brush_dist = length(brush_uv - vec2(0.5, 0.5));

  // Generate brush color procedurally
  vec4 brushColor = vec4(0.0, 0.76, 1.0, 0.5); // Blue color with semi-transparency

  // Blend brush color with terrain color
<<<<<<< Updated upstream

  float influence = smoothstep(0.0, 0.5, 0.5 - brush_dist);
  color = mix(terrainColor, brushColor, influence * brushColor.a);

=======
  float influence = smoothstep(0.0, 0.5, 0.5 - brush_dist);
  color = mix(terrainColor, brushColor, influence * brushColor.a);
>>>>>>> Stashed changes
}
