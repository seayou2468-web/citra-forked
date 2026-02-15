import sys

with open("src/core/arm/dyncom/arm_dyncom_interpreter.cpp", "r") as f:
    content = f.read()

# Remove GDB_BP_CHECK from GOTO_NEXT_INST and put it only in DISPATCH
content = content.replace("#define GOTO_NEXT_INST                                                                             \",
                          "#define GOTO_NEXT_INST_NO_GDB                                                                      \")

# Re-define GOTO_NEXT_INST to exclude GDB check for performance
# We will still check it at the start of DISPATCH and periodically
new_goto_next = """#define GOTO_NEXT_INST                                                                             \
    if (num_instrs >= cpu->NumInstrsToExecute)                                                     \
        goto END;                                                                                  \
    num_instrs++;                                                                                  \
    goto* InstLabel[inst_base->idx]
"""

# Find the original definitions and replace them
# This is tricky because of the #if defined
# Let's just replace the usage of GDB_BP_CHECK in the macro.

content = content.replace("    GDB_BP_CHECK;                                                                                  \", "")

# Now ensure GDB_BP_CHECK is called in DISPATCH
content = content.replace("DISPATCH : {", "DISPATCH : {\n    GDB_BP_CHECK;")

with open("src/core/arm/dyncom/arm_dyncom_interpreter.cpp", "w") as f:
    f.write(content)
