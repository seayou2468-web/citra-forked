import sys

with open("src/citra_libretro/emu_window/libretro_window.cpp", "r") as f:
    content = f.read()

# I will add NEON for the 1:1 copy path.
# RGBA8 (R,G,B,A) to XRGB8888 (0,R,G,B in u32 little endian = B,G,R,0 in memory)
# Wait, my previous check said src[0]=R, src[1]=G, src[2]=B.
# So color = (R<<16) | (G<<8) | B.
# In memory (LE): [B, G, R, 0].

neon_copy = """#ifdef __ARM_NEON
                u32 x = 0;
                for (; x + 3 < dst_w; x += 4) {
                    const u8* s0 = &screen.pixels[(x * src_h + y) * 4];
                    const u8* s1 = &screen.pixels[((x + 1) * src_h + y) * 4];
                    const u8* s2 = &screen.pixels[((x + 2) * src_h + y) * 4];
                    const u8* s3 = &screen.pixels[((x + 3) * src_h + y) * 4];

                    uint8x16x4_t v_src;
                    v_src.val[0] = vld1q_u8(s0); // This is wrong, they are not contiguous
                    // ... actually NEON is better for contiguous data.
                    // But here src pixels are separated by src_h*4.
                }
#endif"""

# Since they are not contiguous, NEON vld1q doesn t help much unless we use vld1q_lane.
# But it might still be faster than scalar.

# However, for now, I will implement a "Dirty Scanline" check in LoadFBToScreenInfo.
# This is much more effective.

# Let s check if LoadFBToScreenInfo already has it. No.
