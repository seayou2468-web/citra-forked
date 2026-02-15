// Copyright 2023 Citra Emulator Project
// Licensed under GPLv2 or any later version
// Refer to the license.txt file included.

#include "common/color.h"
#include "core/core.h"
#include "core/hw/gpu.h"
#include "core/hw/hw.h"
#include "core/hw/lcd.h"
#include "video_core/renderer_software/renderer_software.h"

namespace SwRenderer {

RendererSoftware::RendererSoftware(Core::System& system, Frontend::EmuWindow& window)
    : VideoCore::RendererBase{system, window, nullptr}, memory{system.Memory()},
      rasterizer{system.Memory()} {}

RendererSoftware::~RendererSoftware() = default;

void RendererSoftware::SwapBuffers() {
    PrepareRenderTarget();
    EndFrame();
}

void RendererSoftware::PrepareRenderTarget() {
    for (u32 i = 0; i < 3; i++) {
        const int fb_id = i == 2 ? 1 : 0;

        u32 lcd_color_addr =
            (fb_id == 0) ? LCD_REG_INDEX(color_fill_top) : LCD_REG_INDEX(color_fill_bottom);
        lcd_color_addr = HW::VADDR_LCD + 4 * lcd_color_addr;
        LCD::Regs::ColorFill color_fill = {0};
        LCD::Read(color_fill.raw, lcd_color_addr);

        if (!color_fill.is_enabled) {
            LoadFBToScreenInfo(i);
        }
    }
}

void RendererSoftware::LoadFBToScreenInfo(int i) {
    const u32 fb_id = i == 2 ? 1 : 0;
    const auto& framebuffer = GPU::g_regs.framebuffer_config[fb_id];
    auto& info = screen_infos[i];

    const PAddr framebuffer_addr =
        framebuffer.active_fb == 0 ? framebuffer.address_left1 : framebuffer.address_left2;
    const s32 bpp = GPU::Regs::BytesPerPixel(framebuffer.color_format);
    const u8* framebuffer_data = memory.GetPhysicalPointer(framebuffer_addr);
    if (!framebuffer_data) return;

    const s32 pixel_stride = framebuffer.stride / bpp;
    info.height = framebuffer.height;
    info.width = pixel_stride;
    info.pixels.resize(info.width * info.height * 4);

    if (framebuffer.color_format == GPU::Regs::PixelFormat::RGBA8) {
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
    } else if (framebuffer.color_format == GPU::Regs::PixelFormat::RGB8) {
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
    } else {
        // Fallback for less common formats
        for (u32 y = 0; y < info.height; y++) {
            for (u32 x = 0; x < info.width; x++) {
                const u8* pixel = framebuffer_data + (y * pixel_stride + pixel_stride - 1 - x) * bpp;
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
    }
}

} // namespace SwRenderer
