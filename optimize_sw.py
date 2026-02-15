import sys

with open("src/video_core/renderer_software/sw_rasterizer.cpp", "r") as f:
    content = f.read()

old_loop = """    for (u16 y = min_y + 8; y < max_y; y += 0x10) {
        const auto process_scanline = [&, y] {
            for (u16 x = min_x + 8; x < max_x; x += 0x10) {
                __builtin_prefetch(&fb, 1, 3);
                // Do not process the pixel if it is inside the scissor box and the scissor mode is
                // set to Exclude.
                if (regs.rasterizer.scissor_test.mode == RasterizerRegs::ScissorMode::Exclude) {
                    if (x >= scissor_x1 && x < scissor_x2 && y >= scissor_y1 && y < scissor_y2) {
                        continue;
                    }
                }

                // Calculate the barycentric coordinates w0, w1 and w2
                const s32 w0 = bias0 + SignedArea(vtxpos[1].xy(), vtxpos[2].xy(), {x, y});
                const s32 w1 = bias1 + SignedArea(vtxpos[2].xy(), vtxpos[0].xy(), {x, y});
                const s32 w2 = bias2 + SignedArea(vtxpos[0].xy(), vtxpos[1].xy(), {x, y});
                const s32 wsum = w0 + w1 + w2;"""

# I need to be careful with the exact wording. The file has:
# "if it's inside" not "if it is inside".
# Let's check the cat output again.
# 311:                // Do not process the pixel if it's inside the scissor box and the scissor mode is

old_loop = """    for (u16 y = min_y + 8; y < max_y; y += 0x10) {
        const auto process_scanline = [&, y] {
            for (u16 x = min_x + 8; x < max_x; x += 0x10) {
                __builtin_prefetch(&fb, 1, 3);
                // Do not process the pixel if it's inside the scissor box and the scissor mode is
                // set to Exclude.
                if (regs.rasterizer.scissor_test.mode == RasterizerRegs::ScissorMode::Exclude) {
                    if (x >= scissor_x1 && x < scissor_x2 && y >= scissor_y1 && y < scissor_y2) {
                        continue;
                    }
                }

                // Calculate the barycentric coordinates w0, w1 and w2
                const s32 w0 = bias0 + SignedArea(vtxpos[1].xy(), vtxpos[2].xy(), {x, y});
                const s32 w1 = bias1 + SignedArea(vtxpos[2].xy(), vtxpos[0].xy(), {x, y});
                const s32 w2 = bias2 + SignedArea(vtxpos[0].xy(), vtxpos[1].xy(), {x, y});
                const s32 wsum = w0 + w1 + w2;"""

new_loop = """    const s32 dw0_dx = static_cast<s32>(static_cast<u16>(vtxpos[1].y)) - static_cast<s32>(static_cast<u16>(vtxpos[2].y));
    const s32 dw1_dx = static_cast<s32>(static_cast<u16>(vtxpos[2].y)) - static_cast<s32>(static_cast<u16>(vtxpos[0].y));
    const s32 dw2_dx = static_cast<s32>(static_cast<u16>(vtxpos[0].y)) - static_cast<s32>(static_cast<u16>(vtxpos[1].y));

    for (u16 y = min_y + 8; y < max_y; y += 0x10) {
        const auto process_scanline = [&, y, dw0_dx, dw1_dx, dw2_dx] {
            s32 w0 = bias0 + SignedArea(vtxpos[1].xy(), vtxpos[2].xy(), {min_x + 8, y});
            s32 w1 = bias1 + SignedArea(vtxpos[2].xy(), vtxpos[0].xy(), {min_x + 8, y});
            s32 w2 = bias2 + SignedArea(vtxpos[0].xy(), vtxpos[1].xy(), {min_x + 8, y});

            for (u16 x = min_x + 8; x < max_x; x += 0x10) {
                __builtin_prefetch(&fb, 1, 3);
                // Do not process the pixel if it's inside the scissor box and the scissor mode is
                // set to Exclude.
                if (regs.rasterizer.scissor_test.mode == RasterizerRegs::ScissorMode::Exclude) {
                    if (x >= scissor_x1 && x < scissor_x2 && y >= scissor_y1 && y < scissor_y2) {
                        w0 += dw0_dx; w1 += dw1_dx; w2 += dw2_dx;
                        continue;
                    }
                }

                // Calculate the barycentric coordinates w0, w1 and w2
                const s32 wsum = w0 + w1 + w2;"""

# And I need to update w0, w1, w2 at the end of the loop.
# I'll replace the whole loop body.

if old_loop in content:
    content = content.replace(old_loop, new_loop)
    # Now add increments at the end of the inner loop
    # The end of the inner loop is after the DrawPixel call.
    # 468:                    fb.DrawPixel(x >> 4, y >> 4, result);
    # 469:                }
    # 470:            }

    old_end = """                if (regs.framebuffer.framebuffer.allow_color_write != 0) {
                    fb.DrawPixel(x >> 4, y >> 4, result);
                }
            }"""
    new_end = """                if (regs.framebuffer.framebuffer.allow_color_write != 0) {
                    fb.DrawPixel(x >> 4, y >> 4, result);
                }
                w0 += dw0_dx; w1 += dw1_dx; w2 += dw2_dx;
            }"""
    content = content.replace(old_end, new_end)
    with open("src/video_core/renderer_software/sw_rasterizer.cpp", "w") as f:
        f.write(content)
    print("Success")
else:
    print("Failed to find loop")
