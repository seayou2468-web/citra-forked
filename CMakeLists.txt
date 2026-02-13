# CMake 3.12 required for 20 to be a valid value for CXX_STANDARD
cmake_minimum_required(VERSION 3.15)

# Don't override the warning flags in MSVC:
cmake_policy(SET CMP0092 NEW)
# Enforce new LTO setting
cmake_policy(SET CMP0069 NEW)
# Honor visibility properties for all targets
# Set the default so subdirectory cmake_minimum_required calls won't unset the policy.
cmake_policy(SET CMP0063 NEW)
set(CMAKE_POLICY_DEFAULT_CMP0063 NEW)

list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/CMakeModules")
list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/externals/cmake-modules")
include(DownloadExternals)
include(CMakeDependentOption)

project(citra LANGUAGES C CXX ASM)

option(ENABLE_LIBRETRO "Enable the LibRetro frontend" ON)
option(CITRA_FORCE_INTERPRETER "Force use of CPU interpreter instead of JIT" OFF)

# Some submodules like to pick their own default build type if not specified.
# Make sure we default to Release build type always, unless the generator has custom types.
if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
    set(CMAKE_BUILD_TYPE "Release" CACHE STRING "Choose the type of build." FORCE)
endif()

if (APPLE)
    if (NOT USE_SYSTEM_MOLTENVK)
        download_moltenvk()
    endif()
    find_library(MOLTENVK_LIBRARY NAMES MoltenVK MoltenVK-static)
    if (NOT MOLTENVK_LIBRARY AND IOS)
        # Try finding it in the extracted directory directly as a fallback for iOS
        file(GLOB_RECURSE MOLTENVK_FALLBACK "${CMAKE_BINARY_DIR}/externals/MoltenVK/*MoltenVK.a" "${CMAKE_BINARY_DIR}/externals/MoltenVK/*libMoltenVK.a" "${CMAKE_BINARY_DIR}/externals/MoltenVK/*/MoltenVK")
        if (MOLTENVK_FALLBACK)
            list(GET MOLTENVK_FALLBACK 0 MOLTENVK_LIBRARY)
        endif()
    endif()
    if (NOT MOLTENVK_LIBRARY)
        message(FATAL_ERROR "Could not find MOLTENVK_LIBRARY using the following names: MoltenVK")
    endif()
    message(STATUS "Using MoltenVK at ${MOLTENVK_LIBRARY}.")

    if (IOS)
        find_library(UIKIT_LIBRARY UIKit REQUIRED)
        find_library(COREGRAPHICS_LIBRARY CoreGraphics REQUIRED)
        find_library(QUARTZCORE_LIBRARY QuartzCore REQUIRED)
        find_library(METAL_LIBRARY Metal REQUIRED)
        find_library(AUDIOTOOLBOX_LIBRARY AudioToolbox REQUIRED)
        find_library(COREAUDIO_LIBRARY CoreAudio REQUIRED)
        find_library(FOUNDATION_LIBRARY Foundation REQUIRED)
        find_library(COREHAPTICS_LIBRARY CoreHaptics REQUIRED)
        find_library(GAME_CONTROLLER_LIBRARY GameController REQUIRED)
        find_library(COREVIDEO_LIBRARY CoreVideo REQUIRED)
        find_library(COREMOTION_LIBRARY CoreMotion REQUIRED)
        find_library(SECURITY_LIBRARY Security REQUIRED)
        set(COCOA_LIBRARY ${UIKIT_LIBRARY} ${COREGRAPHICS_LIBRARY} ${QUARTZCORE_LIBRARY} ${METAL_LIBRARY} ${AUDIOTOOLBOX_LIBRARY} ${COREAUDIO_LIBRARY} ${FOUNDATION_LIBRARY} ${COREHAPTICS_LIBRARY} ${GAME_CONTROLLER_LIBRARY} ${COREVIDEO_LIBRARY} ${COREMOTION_LIBRARY} ${SECURITY_LIBRARY})
    else()
        # Umbrella framework for everything GUI-related
        find_library(COCOA_LIBRARY Cocoa REQUIRED)
    endif()

    find_library(AVFOUNDATION_LIBRARY AVFoundation REQUIRED)
    find_library(IOSURFACE_LIBRARY IOSurface REQUIRED)
    set(PLATFORM_LIBRARIES ${COCOA_LIBRARY} ${AVFOUNDATION_LIBRARY} ${IOSURFACE_LIBRARY} ${MOLTENVK_LIBRARY})
elseif (WIN32)
    set(PLATFORM_LIBRARIES winmm ws2_32)
    if (MINGW)
        # PSAPI is the Process Status API
        set(PLATFORM_LIBRARIES ${PLATFORM_LIBRARIES} psapi imm32 version crypt32)
    endif()
elseif (CMAKE_SYSTEM_NAME MATCHES "^(Linux|kFreeBSD|GNU|SunOS)$")
    set(PLATFORM_LIBRARIES rt)
endif()

# Setup a custom clang-format target (if clang-format can be found) that will run
# against all the src files. This should be used before making a pull request.
# =======================================================================

set(CLANG_FORMAT_POSTFIX "-15")
find_program(CLANG_FORMAT
    NAMES clang-format${CLANG_FORMAT_POSTFIX}
          clang-format
    PATHS ${PROJECT_BINARY_DIR}/externals)
# if find_program doesn't find it, try to download from externals
if (NOT CLANG_FORMAT AND NOT DISABLE_CLANG_TARGET)
    if (WIN32)
        message(STATUS "Clang format not found! Downloading...")
        set(CLANG_FORMAT "${PROJECT_BINARY_DIR}/externals/clang-format${CLANG_FORMAT_POSTFIX}.exe")
        file(DOWNLOAD
            https://github.com/citra-emu/ext-windows-bin/raw/master/clang-format${CLANG_FORMAT_POSTFIX}.exe
            "${CLANG_FORMAT}" SHOW_PROGRESS
            STATUS DOWNLOAD_SUCCESS)
        if (NOT DOWNLOAD_SUCCESS EQUAL 0)
            message(WARNING "Could not download clang format! Disabling the clang format target")
            file(REMOVE ${CLANG_FORMAT})
            unset(CLANG_FORMAT)
        endif()
    else()
        message(WARNING "Clang format not found! Disabling the clang format target")
    endif()
endif()

if (CLANG_FORMAT)
    set(SRCS ${PROJECT_SOURCE_DIR}/src)
    set(CCOMMENT "Running clang format against all the .h and .cpp files in src/")
    if (WIN32)
        if(MINGW)
            add_custom_target(clang-format
                COMMAND find `cygpath -u ${SRCS}` -iname *.h -o -iname *.cpp -o -iname *.mm | xargs `cygpath -u ${CLANG_FORMAT}` -i
                COMMENT ${CCOMMENT})
        else()
            add_custom_target(clang-format
                COMMAND powershell.exe -Command "Get-ChildItem '${SRCS}/*' -Include *.cpp,*.h,*.mm -Recurse | Foreach {&'${CLANG_FORMAT}' -i $_.fullname}"
                COMMENT ${CCOMMENT})
        endif()
    else()
        add_custom_target(clang-format
            COMMAND find ${SRCS} -iname *.h -o -iname *.cpp -o -iname *.mm | xargs ${CLANG_FORMAT} -i
            COMMENT ${CCOMMENT})
    endif()
    unset(SRCS)
    unset(CCOMMENT)
endif()

# Include source code
# ===================

# This function should be passed a list of all files in a target. It will automatically generate
# file groups following the directory hierarchy, so that the layout of the files in IDEs matches the
# one in the filesystem.
function(create_target_directory_groups target_name)
    # Place any files that aren't in the source list in a separate group so that they don't get in
    # the way.
    source_group("Other Files" REGULAR_EXPRESSION ".")

    get_target_property(target_sources "${target_name}" SOURCES)

    foreach(file_name IN LISTS target_sources)
        get_filename_component(dir_name "${file_name}" PATH)
        # Group names use '\' as a separator even though the entire rest of CMake uses '/'...
        string(REPLACE "/" "\\" group_name "${dir_name}")
        source_group("${group_name}" FILES "${file_name}")
    endforeach()
endfunction()

# Gets a UTC timstamp and sets the provided variable to it
function(get_timestamp _var)
    string(TIMESTAMP timestamp UTC)
    set(${_var} "${timestamp}" PARENT_SCOPE)
endfunction()

# generate git/build information
include(GetGitRevisionDescription)
get_git_head_revision(GIT_REF_SPEC GIT_REV)
git_describe(GIT_DESC --always --long --dirty)
git_branch_name(GIT_BRANCH)
get_timestamp(BUILD_DATE)

# Boost
# Prevent boost from linking against libs when building
add_definitions(-DBOOST_ERROR_CODE_HEADER_ONLY
    -DBOOST_SYSTEM_NO_LIB
    -DBOOST_DATE_TIME_NO_LIB
    -DBOOST_REGEX_NO_LIB
)
if (USE_SYSTEM_BOOST)
    find_package(Boost 1.70.0 COMPONENTS container locale serialization iostreams REQUIRED)
endif()

enable_testing()
add_subdirectory(externals)

# Boost (bundled)
if (NOT USE_SYSTEM_BOOST)
    add_definitions( -DBOOST_ALL_NO_LIB )
    add_library(Boost::boost ALIAS boost)
    add_library(Boost::serialization ALIAS boost_serialization)
    add_library(Boost::iostreams ALIAS boost_iostreams)
endif()

# SDL2
if (ENABLE_SDL2 AND USE_SYSTEM_SDL2)
    find_package(SDL2 REQUIRED)
    add_library(SDL2 INTERFACE)
    target_link_libraries(SDL2 INTERFACE "${SDL2_LIBRARY}")
    target_include_directories(SDL2 INTERFACE "${SDL2_INCLUDE_DIR}")
    add_library(SDL2::SDL2 ALIAS SDL2)
endif()

if (ENABLE_LIBUSB AND USE_SYSTEM_LIBUSB)
    include(FindPkgConfig)
    find_package(LibUSB)
endif()

if (USE_SYSTEM_SOUNDTOUCH)
    include(FindPkgConfig)
    find_package(SoundTouch REQUIRED)
    add_library(SoundTouch INTERFACE)
    target_link_libraries(SoundTouch INTERFACE "${SOUNDTOUCH_LIBRARIES}")
    target_include_directories(SoundTouch INTERFACE "${SOUNDTOUCH_INCLUDE_DIRS}")
endif()

add_subdirectory(src)
add_subdirectory(dist/installer)


# Set citra-qt project or citra project as default StartUp Project in Visual Studio depending on whether QT is enabled or not
if(ENABLE_QT)
    set_property(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR} PROPERTY VS_STARTUP_PROJECT citra-qt)
else()
    set_property(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR} PROPERTY VS_STARTUP_PROJECT citra)
endif()

# Create target for outputting distributable bundles.
if (CITRA_ENABLE_BUNDLE_TARGET)
    include(BundleTarget)
    if (ENABLE_SDL2_FRONTEND)
        bundle_target(citra)
    endif()
    if (ENABLE_QT)
        bundle_target(citra-qt)
    endif()
    if (ENABLE_DEDICATED_ROOM)
        bundle_target(citra-room)
    endif()
endif()

# Installation instructions
# =========================

# Install freedesktop.org metadata files, following those specifications:
# http://standards.freedesktop.org/desktop-entry-spec/desktop-entry-spec-latest.html
# http://standards.freedesktop.org/icon-theme-spec/icon-theme-spec-latest.html
# http://standards.freedesktop.org/shared-mime-info-spec/shared-mime-info-spec-latest.html
if(ENABLE_QT AND UNIX AND NOT APPLE)
    install(FILES "${PROJECT_SOURCE_DIR}/dist/citra-qt.desktop"
            DESTINATION "${CMAKE_INSTALL_PREFIX}/share/applications")
    install(FILES "${PROJECT_SOURCE_DIR}/dist/citra.svg"
            DESTINATION "${CMAKE_INSTALL_PREFIX}/share/icons/hicolor/scalable/apps")
    install(FILES "${PROJECT_SOURCE_DIR}/dist/citra.xml"
            DESTINATION "${CMAKE_INSTALL_PREFIX}/share/mime/packages")
endif()

if(UNIX)
    if(ENABLE_SDL2)
        install(FILES "${PROJECT_SOURCE_DIR}/dist/citra.6"
                DESTINATION "${CMAKE_INSTALL_PREFIX}/share/man/man6")
    endif()

    if (ENABLE_QT)
        install(FILES "${PROJECT_SOURCE_DIR}/dist/citra-qt.6"
                DESTINATION "${CMAKE_INSTALL_PREFIX}/share/man/man6")
    endif()
endif()
