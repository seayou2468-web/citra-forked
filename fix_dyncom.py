import sys

with open("src/core/arm/dyncom/arm_dyncom_interpreter.cpp", "r") as f:
    content = f.read()

old_gdb = """#define GDB_BP_CHECK                                                                               \
    if (__builtin_expect(GDBStub::IsServerEnabled(), 0)) {                                         \
        cpu->Cpsr = (cpu->Cpsr & 0x0fffffdf) | (cpu->TFlag << 5);                                  \
        if (GDBStub::IsMemoryBreak()) {                                                            \
            goto END;                                                                              \
        } else if (breakpoint_data.type != GDBStub::BreakpointType::None &&                        \
                   PC == breakpoint_data.address) {                                                \
            cpu->RecordBreak(breakpoint_data);                                                     \
            goto END;                                                                              \
        }                                                                                          \
    }"""

new_gdb = """#define GDB_BP_CHECK                                                                               \
    cpu->Cpsr = (cpu->Cpsr & 0x0fffffdf) | (cpu->TFlag << 5);                                      \
    if (__builtin_expect(GDBStub::IsServerEnabled(), 0)) {                                         \
        if (GDBStub::IsMemoryBreak()) {                                                            \
            goto END;                                                                              \
        } else if (breakpoint_data.type != GDBStub::BreakpointType::None &&                        \
                   PC == breakpoint_data.address) {                                                \
            cpu->RecordBreak(breakpoint_data);                                                     \
            goto END;                                                                              \
        }                                                                                              }"""

# Wait, I missed a backslash in new_gdb for the last line of the block.
# And I should use the same format as the original.

new_gdb = """#define GDB_BP_CHECK                                                                               \
    cpu->Cpsr = (cpu->Cpsr & 0x0fffffdf) | (cpu->TFlag << 5);                                      \
    if (__builtin_expect(GDBStub::IsServerEnabled(), 0)) {                                         \
        if (GDBStub::IsMemoryBreak()) {                                                            \
            goto END;                                                                              \
        } else if (breakpoint_data.type != GDBStub::BreakpointType::None &&                        \
                   PC == breakpoint_data.address) {                                                \
            cpu->RecordBreak(breakpoint_data);                                                     \
            goto END;                                                                              \
        }                                                                                          \
    }"""

if old_gdb in content:
    content = content.replace(old_gdb, new_gdb)
    with open("src/core/arm/dyncom/arm_dyncom_interpreter.cpp", "w") as f:
        f.write(content)
    print("Success")
else:
    print("Failed to find GDB_BP_CHECK")
