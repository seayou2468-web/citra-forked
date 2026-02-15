import sys

with open("src/video_core/renderer_software/sw_rasterizer.cpp", "r") as f:
    content = f.read()

# Fix increments (multiply by 16)
content = content.replace(
    "const s32 dw0_dx = static_cast<s32>(static_cast<u16>(vtxpos[1].y)) - static_cast<s32>(static_cast<u16>(vtxpos[2].y));",
    "const s32 dw0_dx = (static_cast<s32>(static_cast<u16>(vtxpos[1].y)) - static_cast<s32>(static_cast<u16>(vtxpos[2].y))) << 4;"
)
content = content.replace(
    "const s32 dw1_dx = static_cast<s32>(static_cast<u16>(vtxpos[2].y)) - static_cast<s32>(static_cast<u16>(vtxpos[0].y));",
    "const s32 dw1_dx = (static_cast<s32>(static_cast<u16>(vtxpos[2].y)) - static_cast<s32>(static_cast<u16>(vtxpos[0].y))) << 4;"
)
content = content.replace(
    "const s32 dw2_dx = static_cast<s32>(static_cast<u16>(vtxpos[0].y)) - static_cast<s32>(static_cast<u16>(vtxpos[1].y));",
    "const s32 dw2_dx = (static_cast<s32>(static_cast<u16>(vtxpos[0].y)) - static_cast<s32>(static_cast<u16>(vtxpos[1].y))) << 4;"
)

with open("src/video_core/renderer_software/sw_rasterizer.cpp", "w") as f:
    f.write(content)
