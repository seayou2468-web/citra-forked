import sys

with open("src/video_core/renderer_software/renderer_software.cpp", "r") as f:
    content = f.read()

# Optimize RGBA8 path
old_rgba8 = """    if (framebuffer.color_format == GPU::Regs::PixelFormat::RGBA8) {
        for (u32 y = 0; y < info.height; y++) {
            const u8* src_line = framebuffer_data + (y * pixel_stride + pixel_stride - 1) * bpp;
            for (u32 x = 0; x < info.width; x++) {
                const u8* pixel = src_line - x * bpp;
                u8* dest = info.pixels.data() + (x * info.height + y) * 4;
                dest[0] = pixel[3];
                dest[1] = pixel[2];
                dest[2] = pixel[1];
                dest[3] = pixel[0];
            }
        }
    }"""

new_rgba8 = """    if (framebuffer.color_format == GPU::Regs::PixelFormat::RGBA8) {
        for (u32 x = 0; x < info.width; x++) {
            for (u32 y = 0; y < info.height; y++) {
                const u8* pixel = framebuffer_data + (y * pixel_stride + pixel_stride - 1 - x) * bpp;
                u8* dest = info.pixels.data() + (x * info.height + y) * 4;
                dest[0] = pixel[3];
                dest[1] = pixel[2];
                dest[2] = pixel[1];
                dest[3] = pixel[0];
            }
        }
    }"""

# Optimize RGB8 path
old_rgb8 = """    } else if (framebuffer.color_format == GPU::Regs::PixelFormat::RGB8) {
        for (u32 y = 0; y < info.height; y++) {
            const u8* src_line = framebuffer_data + (y * pixel_stride + pixel_stride - 1) * bpp;
            for (u32 x = 0; x < info.width; x++) {
                const u8* pixel = src_line - x * bpp;
                u8* dest = info.pixels.data() + (x * info.height + y) * 4;
                dest[0] = pixel[2];
                dest[1] = pixel[1];
                dest[2] = pixel[0];
                dest[3] = 255;
            }
        }
    }"""

new_rgb8 = """    } else if (framebuffer.color_format == GPU::Regs::PixelFormat::RGB8) {
        for (u32 x = 0; x < info.width; x++) {
            for (u32 y = 0; y < info.height; y++) {
                const u8* pixel = framebuffer_data + (y * pixel_stride + pixel_stride - 1 - x) * bpp;
                u8* dest = info.pixels.data() + (x * info.height + y) * 4;
                dest[0] = pixel[2];
                dest[1] = pixel[1];
                dest[2] = pixel[0];
                dest[3] = 255;
            }
        }
    }"""

content = content.replace(old_rgba8, new_rgba8)
content = content.replace(old_rgb8, new_rgb8)

with open("src/video_core/renderer_software/renderer_software.cpp", "w") as f:
    f.write(content)
