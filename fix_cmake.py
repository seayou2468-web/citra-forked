import sys

with open('CMakeLists.txt', 'r') as f:
    lines = f.readlines()

new_lines = []
skip = False
for line in lines:
    if 'if (IOS)' in line:
        new_lines.append(line)
        new_lines.append('        # Minimum iOS 14\n')
        new_lines.append('        set(CMAKE_OSX_DEPLOYMENT_TARGET "14.0")\n')
        new_lines.append('        set(CITRA_FORCE_INTERPRETER ON CACHE BOOL "Force use of CPU interpreter instead of JIT" FORCE)\n')
        new_lines.append('        set(ENABLE_LIBRETRO ON CACHE BOOL "Enable the LibRetro frontend" FORCE)\n\n')
        new_lines.append('        # iOS-specific build settings\n')
        new_lines.append('        set(CMAKE_XCODE_ATTRIBUTE_CODE_SIGNING_ALLOWED NO CACHE STRING "")\n')
        new_lines.append('        set(CMAKE_XCODE_ATTRIBUTE_CODE_SIGN_IDENTITY "" CACHE STRING "")\n')
        new_lines.append('        set(CMAKE_OSX_SYSROOT "iphoneos" CACHE STRING "")\n')
        new_lines.append('        set(CMAKE_OSX_ARCHITECTURES "arm64" CACHE STRING "")\n\n')
        new_lines.append('        # Enable searching CMAKE_PREFIX_PATH for bundled dependencies.\n')
        new_lines.append('        set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY BOTH)\n')
        new_lines.append('        set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE BOTH)\n')
        new_lines.append('        set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE BOTH)\n')
        new_lines.append('    else()\n')
        new_lines.append('        # Minimum macOS 11\n')
        new_lines.append('        set(CMAKE_OSX_DEPLOYMENT_TARGET "11.0")\n')
        new_lines.append('    endif()\n')
        skip = True
    elif skip:
        if 'if (CMAKE_BUILD_TYPE STREQUAL Debug)' in line:
            new_lines.append('endif()\n\n')
            new_lines.append(line)
            skip = False
        else:
            continue
    else:
        new_lines.append(line)

with open('CMakeLists.txt', 'w') as f:
    f.writelines(new_lines)
