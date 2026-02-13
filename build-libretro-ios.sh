#!/bin/bash

set -e

cd $(dirname $0)
mkdir -p build-ios && cd build-ios
cmake -GNinja \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_SYSTEM_NAME=iOS \
    -DCMAKE_OSX_ARCHITECTURES=arm64 \
    -DCMAKE_OSX_SYSROOT=iphoneos \
    -DCMAKE_XCODE_ATTRIBUTE_CODE_SIGNING_ALLOWED=NO \
    -DCMAKE_XCODE_ATTRIBUTE_CODE_SIGN_IDENTITY="" \
    -DCMAKE_POLICY_VERSION_MINIMUM=3.5 \
    -DENABLE_LIBRETRO=ON \
    -DCITRA_FORCE_INTERPRETER=ON \
    -DENABLE_TESTS=OFF -DENABLE_DEDICATED_ROOM=OFF \
    -DENABLE_SDL2=OFF -DENABLE_QT=OFF -DENABLE_WEB_SERVICE=OFF -DENABLE_SCRIPTING=OFF \
    -DENABLE_OPENAL=OFF -DENABLE_LIBUSB=OFF -DCITRA_ENABLE_BUNDLE_TARGET=OFF \
    ..
ninja -j$(sysctl -n hw.ncpu)

SO=citra_libretro_ios.dylib
if [ ! -f "$SO" ]; then
    echo "Error: $SO not found. Checking if it was named differently..."
    ls -l *.dylib
fi
echo "Core file is here => $(readlink -f $SO)"
strip -S $SO
