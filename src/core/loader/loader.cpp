// Copyright 2014 Citra Emulator Project
// Licensed under GPLv2 or any later version
// Refer to the license.txt file included.

#include <memory>
#include <string>
#include "common/logging/log.h"
#include "common/string_util.h"
#include "core/core.h"
#include "core/file_sys/cia_container.h"
#include "core/hle/kernel/process.h"
#include "core/loader/3dsx.h"
#include "core/loader/elf.h"
#include "core/loader/ncch.h"

namespace Loader {

static FileType IdentifyFile_CIA(FileUtil::IOFile& file) {
    u32 magic;
    file.Seek(0, SEEK_SET);
    if (file.ReadBytes(&magic, 4) != 4) return FileType::Unknown;
    if (magic == 0x2020 || magic == 0x2000) return FileType::CIA;
    return FileType::Unknown;
}

FileType IdentifyFile(FileUtil::IOFile& file) {
    FileType type;

#define CHECK_TYPE(loader)                                                                         \
    type = AppLoader_##loader::IdentifyType(&file);                                                \
    if (FileType::Error != type)                                                                   \
        return type;

    CHECK_TYPE(THREEDSX)
    CHECK_TYPE(ELF)
    CHECK_TYPE(NCCH)

    if (IdentifyFile_CIA(file) != FileType::Unknown) return FileType::CIA;

    auto magic_zstd = FileUtil::Z3DSReadIOFile::GetUnderlyingFileMagic(&file);
    if (magic_zstd) {
        if (*magic_zstd == 0x2020 || *magic_zstd == 0x2000) return FileType::CIA;
    }

#undef CHECK_TYPE

    return FileType::Unknown;
}

FileType IdentifyFile(const std::string& file_name) {
    FileUtil::IOFile file(file_name, "rb");
    if (!file.IsOpen()) {
        LOG_ERROR(Loader, "Failed to load file {}", file_name);
        return FileType::Unknown;
    }

    return IdentifyFile(file);
}

FileType GuessFromExtension(const std::string& extension_) {
    std::string extension = Common::ToLower(extension_);

    if (extension == ".elf" || extension == ".axf")
        return FileType::ELF;

    if (extension == ".cci" || extension == ".3ds" || extension == ".zcci")
        return FileType::CCI;

    if (extension == ".cxi" || extension == ".app" || extension == ".zcxi")
        return FileType::CXI;

    if (extension == ".3dsx" || extension == ".z3dsx")
        return FileType::THREEDSX;

    if (extension == ".cia" || extension == ".zcia")
        return FileType::CIA;

    return FileType::Unknown;
}

const char* GetFileTypeString(FileType type, bool is_compressed) {
    switch (type) {
    case FileType::CCI:
        return is_compressed ? "NCSD (Z)" : "NCSD";
    case FileType::CXI:
        return is_compressed ? "NCCH (Z)" : "NCCH";
    case FileType::CIA:
        return is_compressed ? "CIA (Z)" : "CIA";
    case FileType::ELF:
        return "ELF";
    case FileType::THREEDSX:
        return is_compressed ? "3DSX (Z)" : "3DSX";
    default:
        return "Unknown";
    }
}

static std::unique_ptr<AppLoader> GetFileLoader(Core::System& system, std::unique_ptr<FileUtil::IOFile> file,
                                                FileType type, const std::string& filename,
                                                const std::string& filepath) {
    switch (type) {
    case FileType::CCI:
    case FileType::CXI:
        return std::make_unique<AppLoader_NCCH>(system, std::move(file), filepath);
    case FileType::CIA: {
        FileSys::CIAContainer cia;
        if (cia.Load(filepath) == ResultStatus::Success) {
            return std::make_unique<AppLoader_NCCH>(system, std::move(file), filepath, static_cast<u32>(cia.GetContentOffset(0)));
        }
        return std::make_unique<AppLoader_NCCH>(system, std::move(file), filepath, 0);
    }
    case FileType::THREEDSX:
        return std::make_unique<AppLoader_THREEDSX>(system, std::move(file), filename, filepath);
    case FileType::ELF:
        return std::make_unique<AppLoader_ELF>(system, std::move(file), filename);
    default:
        return nullptr;
    }
}

std::unique_ptr<AppLoader> GetLoader(const std::string& filename) {
    auto file = std::make_unique<FileUtil::IOFile>(filename, "rb");
    if (!file->IsOpen()) {
        LOG_ERROR(Loader, "Failed to load file {}", filename);
        return nullptr;
    }

    std::string filename_filename, filename_extension;
    Common::SplitPath(filename, nullptr, &filename_filename, &filename_extension);

    FileType type = IdentifyFile(*file);
    FileType filename_type = GuessFromExtension(filename_extension);

    if (type != filename_type) {
        LOG_WARNING(Loader, "File {} has a different type than its extension.", filename);
        if (FileType::Unknown == type)
            type = filename_type;
    }

    bool is_compressed = false;
    u32 magic;
    file->Seek(0, SEEK_SET);
    if (file->ReadBytes(&magic, 4) == 4 && magic == FileUtil::MakeMagic('Z', '3', 'D', 'S')) {
        is_compressed = true;
        file = std::make_unique<FileUtil::Z3DSReadIOFile>(std::move(file));
    }

    LOG_DEBUG(Loader, "Loading file {} as {}...", filename, GetFileTypeString(type, is_compressed));

    auto& system = Core::System::GetInstance();
    return GetFileLoader(system, std::move(file), type, filename_filename, filename);
}

} // namespace Loader
