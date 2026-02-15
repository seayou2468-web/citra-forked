import sys

with open("src/citra_libretro/citra_libretro.cpp", "r") as f:
    content = f.read()

old_block = """    if (load_result == Core::System::ResultStatus::Success) {
        emu_instance->emu_window->UpdateLayout();
        emu_instance->emu_window->SwapBuffers();
    }"""

new_block = """    if (load_result == Core::System::ResultStatus::Success && emu_instance->emu_window) {
        emu_instance->emu_window->UpdateLayout();
        emu_instance->emu_window->SwapBuffers();
    }"""

if old_block in content:
    content = content.replace(old_block, new_block)
    with open("src/citra_libretro/citra_libretro.cpp", "w") as f:
        f.write(content)
    print("Success")
else:
    print("Failed to find block")
