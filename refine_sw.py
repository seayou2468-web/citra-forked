import sys

with open("src/video_core/renderer_software/sw_rasterizer.cpp", "r") as f:
    content = f.read()

old_check = "if (w0 < 0 || w1 < 0 || w2 < 0) {"
new_check = "if (__builtin_expect((w0 | w1 | w2) < 0, 0)) {"

if old_check in content:
    content = content.replace(old_check, new_check)
    with open("src/video_core/renderer_software/sw_rasterizer.cpp", "w") as f:
        f.write(content)
    print("Success")
else:
    print("Failed to find check")
