import sys

with open("src/video_core/renderer_software/sw_rasterizer.cpp", "r") as f:
    content = f.read()

content = content.replace("get_interpolated_attribute(v0.tc0_w, v1.tc0_w, v2.tc0_w)",
                          "f24::FromFloat32(get_interpolated_attribute_fast(v0.tc0_w.ToFloat32(), v1.tc0_w.ToFloat32(), v2.tc0_w.ToFloat32()))")

content = content.replace("get_interpolated_attribute(v0.quat.x, v1.quat.x, v2.quat.x).ToFloat32()",
                          "get_interpolated_attribute_fast(v0.quat.x.ToFloat32(), v1.quat.x.ToFloat32(), v2.quat.x.ToFloat32())")
content = content.replace("get_interpolated_attribute(v0.quat.y, v1.quat.y, v2.quat.y).ToFloat32()",
                          "get_interpolated_attribute_fast(v0.quat.y.ToFloat32(), v1.quat.y.ToFloat32(), v2.quat.y.ToFloat32())")
content = content.replace("get_interpolated_attribute(v0.quat.z, v1.quat.z, v2.quat.z).ToFloat32()",
                          "get_interpolated_attribute_fast(v0.quat.z.ToFloat32(), v1.quat.z.ToFloat32(), v2.quat.z.ToFloat32())")
content = content.replace("get_interpolated_attribute(v0.quat.w, v1.quat.w, v2.quat.w).ToFloat32()",
                          "get_interpolated_attribute_fast(v0.quat.w.ToFloat32(), v1.quat.w.ToFloat32(), v2.quat.w.ToFloat32())")

content = content.replace("get_interpolated_attribute(v0.view.x, v1.view.x, v2.view.x).ToFloat32()",
                          "get_interpolated_attribute_fast(v0.view.x.ToFloat32(), v1.view.x.ToFloat32(), v2.view.x.ToFloat32())")
content = content.replace("get_interpolated_attribute(v0.view.y, v1.view.y, v2.view.y).ToFloat32()",
                          "get_interpolated_attribute_fast(v0.view.y.ToFloat32(), v1.view.y.ToFloat32(), v2.view.y.ToFloat32())")
content = content.replace("get_interpolated_attribute(v0.view.z, v1.view.z, v2.view.z).ToFloat32()",
                          "get_interpolated_attribute_fast(v0.view.z.ToFloat32(), v1.view.z.ToFloat32(), v2.view.z.ToFloat32())")

with open("src/video_core/renderer_software/sw_rasterizer.cpp", "w") as f:
    f.write(content)
