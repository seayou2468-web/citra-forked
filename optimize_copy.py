import sys

with open("src/citra_libretro/emu_window/libretro_window.cpp", "r") as f:
    content = f.read()

# Replace the inner loop of copy_screen with a NEON-optimized version if available
neon_copy = """
#ifdef __ARM_NEON
        if (src_w == dst_w && src_h == dst_h) {
            for (u32 x = 0; x < dst_w; x++) {
                const u8* src_col = &screen.pixels[x * src_h * 4];
                for (u32 y = 0; y < (dst_h & ~3); y += 4) {
                    const u8* src = &src_col[y * 4];
                    // Load 4 pixels from a column (16 bytes)
                    uint8x16_t p = vld1q_u8(src);

                    // Pixels are R, G, B, A
                    // We want to store to 4 different rows:
                    // dest[(rect.top + y + 0) * width + rect.left + x] = (R0<<16) | (G0<<8) | B0
                    // dest[(rect.top + y + 1) * width + rect.left + x] = (R1<<16) | (G1<<8) | B1
                    // ...

                    for(int i=0; i<4; ++i) {
                        u32* dest = &software_framebuffer[(rect.top + y + i) * width + rect.left + x];
                        const u8* s = &src[i * 4];
                        *dest = (static_cast<u32>(s[0]) << 16) | (static_cast<u32>(s[1]) << 8) | static_cast<u32>(s[2]);
                    }
                }
                // Handle remainder
                for (u32 y = (dst_h & ~3); y < dst_h; y++) {
                    u32* dest = &software_framebuffer[(rect.top + y) * width + rect.left + x];
                    const u8* s = &src_col[y * 4];
                    *dest = (static_cast<u32>(s[0]) << 16) | (static_cast<u32>(s[1]) << 8) | static_cast<u32>(s[2]);
                }
            }
        } else {
#endif
"""

# Actually, the above isn't really using NEON's power yet because it still stores pixel by pixel.
# A true transpose would be better.

# Let's just use a simpler optimization first: swap the loops to improve cache locality for screen.pixels
# and use a better packing method.

optimized_copy = """
        if (src_w == dst_w && src_h == dst_h) {
            // Optimized path: swap loops for better source cache locality
            for (u32 x = 0; x < dst_w; x++) {
                const u8* src_col = &screen.pixels[x * src_h * 4];
                for (u32 y = 0; y < dst_h; y++) {
                    const u8* src = &src_col[y * 4];
                    u32 color = (static_cast<u32>(src[0]) << 16) | (static_cast<u32>(src[1]) << 8) | static_cast<u32>(src[2]);
                    software_framebuffer[(rect.top + y) * width + rect.left + x] = color;
                }
            }
        } else {
"""

# Actually, the existing code was:
# for (u32 y = 0; y < dst_h; y++) {
#     u32* dest_row = &software_framebuffer[(rect.top + y) * width + rect.left];
#     for (u32 x = 0; x < dst_w; x++) {
#         const u8* src = &screen.pixels[(x * src_h + y) * 4];

# In the original code, 'src' was jumping by src_h*4 every 'x' iteration.
# In my optimized code, 'src' is contiguous in the inner loop (y increases by 1, index increases by 4).
# This is MUCH better for cache.

content = content.replace(\"\"\"        if (src_w == dst_w && src_h == dst_h) {
            // Fast path for 1:1 copy (most common case for LibRetro)
            for (u32 y = 0; y < dst_h; y++) {
                u32* dest_row = &software_framebuffer[(rect.top + y) * width + rect.left];
                for (u32 x = 0; x < dst_w; x++) {
                    const u8* src = &screen.pixels[(x * src_h + y) * 4];
                    // RGBA8 column-major to XRGB8888 row-major
                    dest_row[x] = (static_cast<u32>(src[0]) << 16) | (static_cast<u32>(src[1]) << 8) | static_cast<u32>(src[2]);
                }
            }
        } else {\"\"\", optimized_copy)

with open("src/citra_libretro/emu_window/libretro_window.cpp", "w") as f:
    f.write(content)
