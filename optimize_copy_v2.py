import sys

with open("src/citra_libretro/emu_window/libretro_window.cpp", "r") as f:
    content = f.read()

search_text = """        if (src_w == dst_w && src_h == dst_h) {
            // Fast path for 1:1 copy (most common case for LibRetro)
            for (u32 y = 0; y < dst_h; y++) {
                u32* dest_row = &software_framebuffer[(rect.top + y) * width + rect.left];
                for (u32 x = 0; x < dst_w; x++) {
                    const u8* src = &screen.pixels[(x * src_h + y) * 4];
                    // RGBA8 column-major to XRGB8888 row-major
                    dest_row[x] = (static_cast<u32>(src[0]) << 16) | (static_cast<u32>(src[1]) << 8) | static_cast<u32>(src[2]);
                }
            }
        } else {"""

replace_text = """        if (src_w == dst_w && src_h == dst_h) {
            // Optimized path: swap loops for better source cache locality
            for (u32 x = 0; x < dst_w; x++) {
                const u8* src_col = &screen.pixels[x * src_h * 4];
                for (u32 y = 0; y < dst_h; y++) {
                    const u8* src = &src_col[y * 4];
                    u32 color = (static_cast<u32>(src[0]) << 16) | (static_cast<u32>(src[1]) << 8) | static_cast<u32>(src[2]);
                    software_framebuffer[(rect.top + y) * width + rect.left + x] = color;
                }
            }
        } else {"""

if search_text in content:
    content = content.replace(search_text, replace_text)
    with open("src/citra_libretro/emu_window/libretro_window.cpp", "w") as f:
        f.write(content)
    print("Successfully optimized CopySoftwareFramebuffer")
else:
    print("Search text not found")
