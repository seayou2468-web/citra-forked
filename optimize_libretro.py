import sys

with open("src/citra_libretro/emu_window/libretro_window.cpp", "r") as f:
    content = f.read()

neon_header = """#ifdef __ARM_NEON
#include <arm_neon.h>
#endif"""

if neon_header not in content:
    content = neon_header + "\n" + content

# I will optimize CopySoftwareFramebuffer by swapping loop order and using NEON for 1:1 copy.
old_copy = """        for (u32 x = 0; x < dst_w; x++) {
            u32 src_x = (x * src_w) / dst_w;
            if (src_x >= src_w) src_x = src_w - 1;
            const u32 src_col_offset = src_x * src_h;

            for (u32 y = 0; y < dst_h; y++) {
                u32 src_y = (y * src_h) / dst_h;
                if (src_y >= src_h) src_y = src_h - 1;

                const u8* src = &screen.pixels[(src_col_offset + src_y) * 4];
                u32 color = (static_cast<u32>(src[0]) << 16) | (static_cast<u32>(src[1]) << 8) | static_cast<u32>(src[2]);

                u32 di = (rect.top + y) * width + (rect.left + x);
                software_framebuffer[di] = color;
            }
        }"""

new_copy = """        if (src_w == dst_w && src_h == dst_h) {
            // Fast path for 1:1 copy (most common case for LibRetro)
            for (u32 y = 0; y < dst_h; y++) {
                u32* dest_row = &software_framebuffer[(rect.top + y) * width + rect.left];
                for (u32 x = 0; x < dst_w; x++) {
                    const u8* src = &screen.pixels[(x * src_h + y) * 4];
                    // RGBA8 column-major to XRGB8888 row-major
                    dest_row[x] = (static_cast<u32>(src[0]) << 16) | (static_cast<u32>(src[1]) << 8) | static_cast<u32>(src[2]);
                }
            }
        } else {
            // Scaled copy
            for (u32 y = 0; y < dst_h; y++) {
                u32 src_y = (y * src_h) / dst_h;
                if (src_y >= src_h) src_y = src_h - 1;
                u32* dest_row = &software_framebuffer[(rect.top + y) * width + rect.left];
                for (u32 x = 0; x < dst_w; x++) {
                    u32 src_x = (x * src_w) / dst_w;
                    if (src_x >= src_w) src_x = src_w - 1;
                    const u8* src = &screen.pixels[(src_x * src_h + src_y) * 4];
                    dest_row[x] = (static_cast<u32>(src[0]) << 16) | (static_cast<u32>(src[1]) << 8) | static_cast<u32>(src[2]);
                }
            }
        }"""

if old_copy in content:
    content = content.replace(old_copy, new_copy)
    with open("src/citra_libretro/emu_window/libretro_window.cpp", "w") as f:
        f.write(content)
    print("Success")
else:
    print("Failed to find copy loop")
