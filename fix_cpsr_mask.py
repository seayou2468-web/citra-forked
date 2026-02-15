import sys

with open("src/core/arm/dyncom/arm_dyncom_interpreter.cpp", "r") as f:
    content = f.read()

# Fix the mask in GDB_BP_CHECK
content = content.replace("0x0fffffdf", "0xfffffffdf")
# Wait, too many f s? 0x FFFF FFDF (8 hex digits).
# My previous one was 0x 0FFF FFDF (8 hex digits).
# It should be 0xFFFFFFDF.

content = content.replace("0x0fffffdf", "0xffffffdf")

with open("src/core/arm/dyncom/arm_dyncom_interpreter.cpp", "w") as f:
    f.write(content)
