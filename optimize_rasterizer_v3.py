import sys
import re

with open("src/video_core/renderer_software/sw_rasterizer.cpp", "r") as f:
    content = f.read()

# Replace multi-line get_interpolated_attribute calls
content = re.sub(r"get_interpolated_attribute\(v0\.color\.r\(\), v1\.color\.r\(\), v2\.color\.r\(\)\)\s+\.ToFloat32\(\)",
                 "get_interpolated_attribute_fast(v0.color.r().ToFloat32(), v1.color.r().ToFloat32(), v2.color.r().ToFloat32())",
                 content, flags=re.MULTILINE)
content = re.sub(r"get_interpolated_attribute\(v0\.color\.g\(\), v1\.color\.g\(\), v2\.color\.g\(\)\)\s+\.ToFloat32\(\)",
                 "get_interpolated_attribute_fast(v0.color.g().ToFloat32(), v1.color.g().ToFloat32(), v2.color.g().ToFloat32())",
                 content, flags=re.MULTILINE)
content = re.sub(r"get_interpolated_attribute\(v0\.color\.b\(\), v1\.color\.b\(\), v2\.color\.b\(\)\)\s+\.ToFloat32\(\)",
                 "get_interpolated_attribute_fast(v0.color.b().ToFloat32(), v1.color.b().ToFloat32(), v2.color.b().ToFloat32())",
                 content, flags=re.MULTILINE)
content = re.sub(r"get_interpolated_attribute\(v0\.color\.a\(\), v1\.color\.a\(\), v2\.color\.a\(\)\)\s+\.ToFloat32\(\)",
                 "get_interpolated_attribute_fast(v0.color.a().ToFloat32(), v1.color.a().ToFloat32(), v2.color.a().ToFloat32())",
                 content, flags=re.MULTILINE)

content = re.sub(r"get_interpolated_attribute\(v0\.quat\.x, v1\.quat\.x, v2\.quat\.x\)\s+\.ToFloat32\(\)",
                 "get_interpolated_attribute_fast(v0.quat.x.ToFloat32(), v1.quat.x.ToFloat32(), v2.quat.x.ToFloat32())",
                 content, flags=re.MULTILINE)
content = re.sub(r"get_interpolated_attribute\(v0\.quat\.y, v1\.quat\.y, v2\.quat\.y\)\s+\.ToFloat32\(\)",
                 "get_interpolated_attribute_fast(v0.quat.y.ToFloat32(), v1.quat.y.ToFloat32(), v2.quat.y.ToFloat32())",
                 content, flags=re.MULTILINE)
content = re.sub(r"get_interpolated_attribute\(v0\.quat\.z, v1\.quat\.z, v2\.quat\.z\)\s+\.ToFloat32\(\)",
                 "get_interpolated_attribute_fast(v0.quat.z.ToFloat32(), v1.quat.z.ToFloat32(), v2.quat.z.ToFloat32())",
                 content, flags=re.MULTILINE)

with open("src/video_core/renderer_software/sw_rasterizer.cpp", "w") as f:
    f.write(content)
