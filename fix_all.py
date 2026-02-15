import sys

# 1. Fix CPSR mask in dyncom
with open("src/core/arm/dyncom/arm_dyncom_interpreter.cpp", "r") as f:
    content = f.read()
content = content.replace("0x0fffffdf", "0xffffffdf")
with open("src/core/arm/dyncom/arm_dyncom_interpreter.cpp", "w") as f:
    f.write(content)

# 2. Fix sign extension in sw_rasterizer
with open("src/video_core/renderer_software/sw_rasterizer.cpp", "r") as f:
    content = f.read()
content = content.replace(
    "static_cast<s32>(static_cast<u16>(vtxpos[1].y))",
    "static_cast<s32>(static_cast<s16>(static_cast<u16>(vtxpos[1].y)))"
)
content = content.replace(
    "static_cast<s32>(static_cast<u16>(vtxpos[2].y))",
    "static_cast<s32>(static_cast<s16>(static_cast<u16>(vtxpos[2].y)))"
)
content = content.replace(
    "static_cast<s32>(static_cast<u16>(vtxpos[0].y))",
    "static_cast<s32>(static_cast<s16>(static_cast<u16>(vtxpos[0].y)))"
)
with open("src/video_core/renderer_software/sw_rasterizer.cpp", "w") as f:
    f.write(content)

# 3. Add null check in renderer_software
with open("src/video_core/renderer_software/renderer_software.cpp", "r") as f:
    lines = f.readlines()
new_lines = []
for line in lines:
    new_lines.append(line)
    if "const u8* framebuffer_data = memory.GetPhysicalPointer(framebuffer_addr);" in line:
        new_lines.append("    if (!framebuffer_data) return;\n")
with open("src/video_core/renderer_software/renderer_software.cpp", "w") as f:
    f.writelines(new_lines)

print("Success")
