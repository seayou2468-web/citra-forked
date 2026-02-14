import re

with open('src/citra_libretro/citra_libretro.cpp', 'r') as f:
    content = f.read()

# Change RunLoop(false) to RunLoop(true)
content = content.replace('Core::System::GetInstance().RunLoop(false)', 'Core::System::GetInstance().RunLoop(true)')

with open('src/citra_libretro/citra_libretro.cpp', 'w') as f:
    f.write(content)
