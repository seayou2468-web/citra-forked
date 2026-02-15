import sys

with open("src/citra_libretro/citra_libretro.cpp", "r") as f:
    lines = f.readlines()

# Fix retro_run
new_lines = []
in_retro_run = False
for i, line in enumerate(lines):
    if "void retro_run()" in line:
        in_retro_run = True

    if in_retro_run and "if (load_result == Core::System::ResultStatus::Success" in line:
        # This is the junk block we added by mistake
        new_lines.append("}\n") # Close retro_run
        in_retro_run = False
        continue

    if in_retro_run and "void context_reset()" in line:
        # Safety catch if we missed the junk block
        new_lines.append("}\n")
        in_retro_run = False

    # In retro_load_game, remove SwapBuffers
    if "emu_instance->emu_window->SwapBuffers();" in line and i > 500:
        continue

    new_lines.append(line)

with open("src/citra_libretro/citra_libretro.cpp", "w") as f:
    f.writelines(new_lines)
