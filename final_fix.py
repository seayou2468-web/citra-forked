import sys

with open("src/video_core/renderer_software/sw_rasterizer.cpp", "r") as f:
    content = f.read()

content = content.replace("interpolated_w_inverse.ToFloat32()", "interp_w_inv")

with open("src/video_core/renderer_software/sw_rasterizer.cpp", "w") as f:
    f.write(content)
