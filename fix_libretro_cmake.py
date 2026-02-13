with open('src/citra_libretro/CMakeLists.txt', 'r') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    new_lines.append(line)
    if 'set_target_properties(citra_libretro PROPERTIES PREFIX "")' in line:
        new_lines.append('if(IOS)\n  set_target_properties(citra_libretro PROPERTIES SUFFIX "_ios.dylib")\nendif()\n')

with open('src/citra_libretro/CMakeLists.txt', 'w') as f:
    f.writelines(new_lines)
