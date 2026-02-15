import sys

with open("src/video_core/renderer_software/sw_rasterizer.cpp", "r") as f:
    content = f.read()

neon_header = """#ifdef __ARM_NEON
#include <arm_neon.h>
#endif"""

if neon_header not in content:
    content = neon_header + "\n" + content

# I'll add a specialized loop for 4 pixels at once using NEON.
# But for now, the incremental barycentric I already added is a good start.
# I'll refine it to use NEON for the 4-pixel calculation.

with open("src/video_core/renderer_software/sw_rasterizer.cpp", "w") as f:
    f.write(content)
