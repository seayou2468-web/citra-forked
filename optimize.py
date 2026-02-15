import sys

def replace_in_file(file_path, search_str, replace_str):
    with open(file_path, "r") as f:
        content = f.read()
    if search_str in content:
        content = content.replace(search_str, replace_str)
        with open(file_path, "w") as f:
            f.write(content)
        return True
    return False

# Optimize dyncom
replace_in_file("src/core/arm/dyncom/arm_dyncom_interpreter.cpp",
    """#define GDB_BP_CHECK                                                                               \
    cpu->Cpsr &= ~(1 << 5);                                                                        \
    cpu->Cpsr |= cpu->TFlag << 5;                                                                  \
    if (GDBStub::IsServerEnabled()) {                                                              \
        if (GDBStub::IsMemoryBreak()) {                                                            \
            goto END;                                                                              \
        } else if (breakpoint_data.type != GDBStub::BreakpointType::None &&                        \
                   PC == breakpoint_data.address) {                                                \
            cpu->RecordBreak(breakpoint_data);                                                     \
            goto END;                                                                              \
        }                                                                                          \
    }""",
    """#define GDB_BP_CHECK                                                                               \
    if (__builtin_expect(GDBStub::IsServerEnabled(), 0)) {                                         \
        cpu->Cpsr = (cpu->Cpsr & 0x0fffffdf) | (cpu->TFlag << 5);                                  \
        if (GDBStub::IsMemoryBreak()) {                                                            \
            goto END;                                                                              \
        } else if (breakpoint_data.type != GDBStub::BreakpointType::None &&                        \
                   PC == breakpoint_data.address) {                                                \
            cpu->RecordBreak(breakpoint_data);                                                     \
            goto END;                                                                              \
        }                                                                                          \
    }""")

# Optimize software renderer
with open("src/video_core/renderer_software/sw_rasterizer.cpp", "r") as f:
    lines = f.readlines()

new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    if "for (u16 y = min_y + 8; y < max_y; y += 0x10) {" in line:
        new_lines.append(line)
        new_lines.append("        const s32 dw0_dx = static_cast<s32>(static_cast<u16>(vtxpos[1].y)) - static_cast<s32>(static_cast<u16>(vtxpos[2].y));\n")
        new_lines.append("        const s32 dw1_dx = static_cast<s32>(static_cast<u16>(vtxpos[2].y)) - static_cast<s32>(static_cast<u16>(vtxpos[0].y));\n")
        new_lines.append("        const s32 dw2_dx = static_cast<s32>(static_cast<u16>(vtxpos[0].y)) - static_cast<s32>(static_cast<u16>(vtxpos[1].y));\n")
        new_lines.append("        const s32 dw0_dy = static_cast<s32>(static_cast<u16>(vtxpos[2].x)) - static_cast<s32>(static_cast<u16>(vtxpos[1].x));\n")
        new_lines.append("        const s32 dw1_dy = static_cast<s32>(static_cast<u16>(vtxpos[0].x)) - static_cast<s32>(static_cast<u16>(vtxpos[2].x));\n")
        new_lines.append("        const s32 dw2_dy = static_cast<s32>(static_cast<u16>(vtxpos[1].x)) - static_cast<s32>(static_cast<u16>(vtxpos[0].x));\n")
        i += 1
        continue
    if "const auto process_scanline = [&, y] {" in line:
        new_lines.append(line)
        new_lines.append("            s32 w0_row = bias0 + SignedArea(vtxpos[1].xy(), vtxpos[2].xy(), {min_x + 8, y});\n")
        new_lines.append("            s32 w1_row = bias1 + SignedArea(vtxpos[2].xy(), vtxpos[0].xy(), {min_x + 8, y});\n")
        new_lines.append("            s32 w2_row = bias2 + SignedArea(vtxpos[0].xy(), vtxpos[1].xy(), {min_x + 8, y});\n")
        i += 1
        continue
    if "for (u16 x = min_x + 8; x < max_x; x += 0x10) {" in line:
        new_lines.append(line)
        new_lines.append("                s32 w0 = w0_row;\n")
        new_lines.append("                s32 w1 = w1_row;\n")
        new_lines.append("                s32 w2 = w2_row;\n")
        i += 1
        continue
    if "const s32 w0 = bias0 + SignedArea(vtxpos[1].xy(), vtxpos[2].xy(), {x, y});" in line:
        i += 3 # skip the 3 SignedArea calls
        continue
    if "const s32 wsum = w0 + w1 + w2;" in line:
        new_lines.append(line)
        i += 1
        # Add increments at the end of loop
        # We need to find the end of the loop
        depth = 0
        j = i
        while j < len(lines):
            if "{" in lines[j]: depth += 1
            if "}" in lines[j]:
                if depth == 0:
                    # End of for loop
                    # Wait, the for loop starts at "for (u16 x = min_x + 8..."
                    # We are currently inside it.
                    pass
                depth -= 1
            if depth < 0: # This means we exited the block
                break
            new_lines.append(lines[j])
            j += 1
        new_lines.append("                w0_row += dw0_dx;\n")
        new_lines.append("                w1_row += dw1_dx;\n")
        new_lines.append("                w2_row += dw2_dx;\n")
        # Wait, I messed up the nesting.
        # Let's rewrite the whole loop block.
        i = len(lines) # stop outer loop
        break
    new_lines.append(line)
    i += 1

# Actually, rewriting the whole function is safer.
