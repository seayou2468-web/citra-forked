import sys

with open("src/video_core/renderer_software/renderer_software.cpp", "r") as f:
    content = f.read()

old_loop = """    for (u32 y = 0; y < info.height; y++) {
        for (u32 x = 0; x < info.width; x++) {
            const u8* pixel = framebuffer_data + (y * pixel_stride + pixel_stride - x) * bpp;
            const Common::Vec4 color = [&] {
                switch (framebuffer.color_format) {
                case GPU::Regs::PixelFormat::RGBA8:
                    return Common::Color::DecodeRGBA8(pixel);
                case GPU::Regs::PixelFormat::RGB8:
                    return Common::Color::DecodeRGB8(pixel);
                case GPU::Regs::PixelFormat::RGB565:
                    return Common::Color::DecodeRGB565(pixel);
                case GPU::Regs::PixelFormat::RGB5A1:
                    return Common::Color::DecodeRGB5A1(pixel);
                case GPU::Regs::PixelFormat::RGBA4:
                    return Common::Color::DecodeRGBA4(pixel);
                }
                UNREACHABLE();
            }();
            const u32 output_offset = (x * info.height + y) * 4;
            u8* dest = info.pixels.data() + output_offset;
            std::memcpy(dest, color.AsArray(), sizeof(color));
        }
    }"""

new_loop = """    if (framebuffer.color_format == GPU::Regs::PixelFormat::RGBA8) {
        for (u32 y = 0; y < info.height; y++) {
            const u8* src_line = framebuffer_data + (y * pixel_stride + pixel_stride) * bpp;
            for (u32 x = 0; x < info.width; x++) {
                const u8* pixel = src_line - x * bpp;
                u8* dest = info.pixels.data() + (x * info.height + y) * 4;
                dest[0] = pixel[3];
                dest[1] = pixel[2];
                dest[2] = pixel[1];
                dest[3] = pixel[0];
            }
        }
    } else if (framebuffer.color_format == GPU::Regs::PixelFormat::RGB8) {
        for (u32 y = 0; y < info.height; y++) {
            const u8* src_line = framebuffer_data + (y * pixel_stride + pixel_stride) * bpp;
            for (u32 x = 0; x < info.width; x++) {
                const u8* pixel = src_line - x * bpp;
                u8* dest = info.pixels.data() + (x * info.height + y) * 4;
                dest[0] = pixel[2];
                dest[1] = pixel[1];
                dest[2] = pixel[0];
                dest[3] = 255;
            }
        }
    } else {
        // Fallback for less common formats
        for (u32 y = 0; y < info.height; y++) {
            for (u32 x = 0; x < info.width; x++) {
                const u8* pixel = framebuffer_data + (y * pixel_stride + pixel_stride - x) * bpp;
                const Common::Vec4 color = [&] {
                    switch (framebuffer.color_format) {
                    case GPU::Regs::PixelFormat::RGB565:
                        return Common::Color::DecodeRGB565(pixel);
                    case GPU::Regs::PixelFormat::RGB5A1:
                        return Common::Color::DecodeRGB5A1(pixel);
                    case GPU::Regs::PixelFormat::RGBA4:
                        return Common::Color::DecodeRGBA4(pixel);
                    default:
                        UNREACHABLE();
                    }
                }();
                const u32 output_offset = (x * info.height + y) * 4;
                u8* dest = info.pixels.data() + output_offset;
                std::memcpy(dest, color.AsArray(), 4);
            }
        }
    }"""

if old_loop in content:
    content = content.replace(old_loop, new_loop)
    with open("src/video_core/renderer_software/renderer_software.cpp", "w") as f:
        f.write(content)
    print("Success")
else:
    print("Failed to find loop")
