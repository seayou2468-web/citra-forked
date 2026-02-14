import re

with open('src/core/loader/loader.cpp', 'r') as f:
    content = f.read()

# Add include
if '#include "core/file_sys/cia_container.h"' not in content:
    content = '#include "core/file_sys/cia_container.h"\n' + content

# Fix GetFileLoader for CIA
cia_fix = r'''    case FileType::CIA: {
        FileSys::CIAContainer cia;
        if (cia.Load(filepath) == ResultStatus::Success) {
            return std::make_unique<AppLoader_NCCH>(std::move(file), filepath, static_cast<u32>(cia.GetContentOffset(0)));
        }
        return std::make_unique<AppLoader_NCCH>(std::move(file), filepath, 0);
    }'''

content = re.sub(r'case FileType::CIA:.*?return std::make_unique<AppLoader_NCCH>\(std::move\(file\), filepath, 0\);',
                 cia_fix, content, flags=re.DOTALL)

with open('src/core/loader/loader.cpp', 'w') as f:
    f.write(content)
