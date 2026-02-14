// Copyright 2017 Citra Emulator Project
// Licensed under GPLv2 or any later version
// Refer to the license.txt file included.

#include <libretro.h>

#include "audio_core/audio_types.h"
#include "citra_libretro/citra_libretro.h"
#include "citra_libretro/environment.h"
#include "citra_libretro/input/input_factory.h"
#include "common/settings.h"
#include "core/3ds.h"
#include "video_core/video_core.h"
#include "video_core/renderer_software/renderer_software.h"




EmuWindow_LibRetro::EmuWindow_LibRetro() {
    strict_context_required = true;
    window_info.type = Frontend::WindowSystemType::LibRetro;
}

EmuWindow_LibRetro::~EmuWindow_LibRetro() {}

void EmuWindow_LibRetro::SwapBuffers() {
    submittedFrame = true;
    CopySoftwareFramebuffer();
    LibRetro::UploadVideoFrame(software_framebuffer.data(),
                            static_cast<unsigned>(width),
                            static_cast<unsigned>(height), width * 4);
}

void EmuWindow_LibRetro::SetupFramebuffer() {}

void EmuWindow_LibRetro::PollEvents() {
    LibRetro::PollInput();

    // TODO: Poll for right click for motion emu

    if (true) {
        tracker->Update(width, height, GetFramebufferLayout().bottom_screen);

        if (tracker->IsPressed()) {
            auto mousePos = tracker->GetPressedPosition();

            if (hasTouched) {
                TouchMoved(mousePos.first, mousePos.second);
            } else {
                TouchPressed(mousePos.first, mousePos.second);
                hasTouched = true;
            }
        } else if (hasTouched) {
            hasTouched = false;
            TouchReleased();
        }
    }
}

void EmuWindow_LibRetro::MakeCurrent() {
    // They don't get any say in the matter - GL context is always current!
}

void EmuWindow_LibRetro::DoneCurrent() {
    // They don't get any say in the matter - GL context is always current!
}

void EmuWindow_LibRetro::OnMinimalClientAreaChangeRequest(std::pair<u32, u32> _minimal_size) {
}

void EmuWindow_LibRetro::UpdateLayout() {
    // TODO: Handle custom layouts
    // TODO: Extract this ugly thing somewhere else
    unsigned baseX;
    unsigned baseY;

    float scaling = Settings::values.resolution_factor.GetValue();

    bool swapped = Settings::values.swap_screen.GetValue();

    enableEmulatedPointer = true;

    switch (Settings::values.layout_option.GetValue()) {
    case Settings::LayoutOption::SingleScreen:
        if (swapped) { // Bottom screen visible
            baseX = Core::kScreenBottomWidth;
            baseY = Core::kScreenBottomHeight;
        } else { // Top screen visible
            baseX = Core::kScreenTopWidth;
            baseY = Core::kScreenTopHeight;
            enableEmulatedPointer = false;
        }
        baseX *= scaling;
        baseY *= scaling;
        break;
    case Settings::LayoutOption::LargeScreen:
        if (swapped) { // Bottom screen biggest
            baseX = Core::kScreenBottomWidth + Core::kScreenTopWidth / 4;
            baseY = Core::kScreenBottomHeight;
        } else { // Top screen biggest
            baseX = Core::kScreenTopWidth + Core::kScreenBottomWidth / 4;
            baseY = Core::kScreenTopHeight;
        }

        if (scaling < 4) {
            // Unfortunately, to get this aspect ratio correct (and have non-blurry 1x scaling),
            //  we have to have a pretty large buffer for the minimum ratio.
            baseX *= 4;
            baseY *= 4;
        } else {
            baseX *= scaling;
            baseY *= scaling;
        }
        break;
    case Settings::LayoutOption::SideScreen:
        baseX = Core::kScreenBottomWidth + Core::kScreenTopWidth;
        baseY = Core::kScreenTopHeight;
        baseX *= scaling;
        baseY *= scaling;
        break;
    case Settings::LayoutOption::Default:
    default:
        baseX = Core::kScreenTopWidth;
        baseY = Core::kScreenTopHeight + Core::kScreenBottomHeight;
        baseX *= scaling;
        baseY *= scaling;
        break;
    }

    // Update Libretro with our status
    struct retro_system_av_info info {};
    info.timing.fps = 60.0;
    info.timing.sample_rate = AudioCore::native_sample_rate;
    info.geometry.aspect_ratio = (float)baseX / (float)baseY;
    info.geometry.base_width = baseX;
    info.geometry.base_height = baseY;
    info.geometry.max_width = baseX;
    info.geometry.max_height = baseY;
    if (!LibRetro::SetGeometry(&info)) {
        LOG_CRITICAL(Frontend, "Failed to update 3DS layout in frontend!");
    }

    width = baseX;
    height = baseY;

    software_framebuffer.resize(width * height);

    UpdateCurrentFramebufferLayout(baseX, baseY);

    doCleanFrame = true;
}

bool EmuWindow_LibRetro::ShouldDeferRendererInit() { return false; }

bool EmuWindow_LibRetro::NeedsClearing() const {
    // We manage this ourselves.
    return false;
}

bool EmuWindow_LibRetro::HasSubmittedFrame() {
    bool state = submittedFrame;
    submittedFrame = false;
    return state;
}

void EmuWindow_LibRetro::CreateContext() {
    tracker = std::make_unique<LibRetro::Input::MouseTracker>();
    doCleanFrame = true;
}

void EmuWindow_LibRetro::DestroyContext() {
    tracker = nullptr;
}

void EmuWindow_LibRetro::CopySoftwareFramebuffer() {
    auto renderer = static_cast<SwRenderer::RendererSoftware*>(VideoCore::g_renderer.get());
    if (!renderer) {
        return;
    }

    const auto& layout = GetFramebufferLayout();

    // Clear buffer
    std::fill(software_framebuffer.begin(), software_framebuffer.end(), 0);

    auto copy_screen = [&](VideoCore::ScreenId id, const Common::Rectangle<u32>& rect) {
        if (rect.GetWidth() == 0 || rect.GetHeight() == 0) {
            return;
        }
        const auto& screen = renderer->Screen(id);
        if (screen.pixels.empty()) {
            return;
        }

        u32 src_w = screen.width;
        u32 src_h = screen.height;
        u32 dst_w = rect.GetWidth();
        u32 dst_h = rect.GetHeight();

        // RendererSoftware outputs are column-major in memory:
        // screen.pixels[ (x * screen.height + y) * 4 ]

        for (u32 x = 0; x < dst_w; x++) {
            u32 src_x = (x * src_w) / dst_w;
            if (src_x >= src_w) src_x = src_w - 1;
            const u32 src_col_offset = src_x * src_h;

            for (u32 y = 0; y < dst_h; y++) {
                u32 src_y = (y * src_h) / dst_h;
                if (src_y >= src_h) src_y = src_h - 1;

                const u8* src = &screen.pixels[(src_col_offset + src_y) * 4];
                u32 color = (static_cast<u32>(src[0]) << 16) | (static_cast<u32>(src[1]) << 8) | static_cast<u32>(src[2]);

                u32 di = (rect.top + y) * width + (rect.left + x);
                software_framebuffer[di] = color;
            }
        }
    };

    copy_screen(VideoCore::ScreenId::TopLeft, layout.top_screen);
    copy_screen(VideoCore::ScreenId::Bottom, layout.bottom_screen);
}
