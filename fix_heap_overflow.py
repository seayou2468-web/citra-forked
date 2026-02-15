import sys

with open("src/video_core/renderer_software/renderer_software.cpp", "r") as f:
    content = f.read()

# Fix RGBA8 loop
content = content.replace(
    "const u8* src_line = framebuffer_data + (y * pixel_stride + pixel_stride) * bpp;",
    "const u8* src_line = framebuffer_data + (y * pixel_stride + pixel_stride - 1) * bpp;"
)

# Fix fallback loop (it was also buggy in original but I should fix it now)
# Original fallback I used:
# const u8* pixel = framebuffer_data + (y * pixel_stride + pixel_stride - x) * bpp;
# Change to:
# const u8* pixel = framebuffer_data + (y * pixel_stride + pixel_stride - 1 - x) * bpp;

content = content.replace(
    "const u8* pixel = framebuffer_data + (y * pixel_stride + pixel_stride - x) * bpp;",
    "const u8* pixel = framebuffer_data + (y * pixel_stride + pixel_stride - 1 - x) * bpp;"
)

with open("src/video_core/renderer_software/renderer_software.cpp", "w") as f:
    f.write(content)
