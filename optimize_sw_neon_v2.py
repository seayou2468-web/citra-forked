import sys

with open("src/video_core/renderer_software/sw_rasterizer.cpp", "r") as f:
    content = f.read()

# I will add NEON skip check for 4 pixels.
# This requires restructuring the loop.
# For now, I will add a comment about it and implement a simpler check.

# Actually, I will implement a "Dirty Scanline" check in LoadFBToScreenInfo.
# It can significantly speed up static screens (like menus).

# But the user asked for "快適に問題なく動作するように".
# I'll implement the "Fast TLB" for dyncom if not already fully used.
# I saw it in ReadMemory32.

with open("src/video_core/renderer_software/sw_rasterizer.cpp", "w") as f:
    f.write(content)
