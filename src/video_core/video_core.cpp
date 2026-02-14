// Copyright 2014 Citra Emulator Project
// Licensed under GPLv2 or any later version
// Refer to the license.txt file included.

#include <memory>
#include "common/archives.h"
#include "common/logging/log.h"
#include "common/settings.h"
#include "core/core.h"
#include "core/frontend/emu_window.h"
#include "video_core/pica.h"
#include "video_core/pica_state.h"
#include "video_core/renderer_base.h"
#include "video_core/renderer_software/renderer_software.h"
#include "video_core/video_core.h"

namespace VideoCore {

std::unique_ptr<RendererBase> g_renderer{}; ///< Renderer plugin

std::atomic<bool> g_shader_jit_enabled = false;
std::atomic<bool> g_hw_shader_enabled = true;
std::atomic<bool> g_hw_shader_accurate_mul = true;

Memory::MemorySystem* g_memory;

/// Initialize the video core
void Init(Frontend::EmuWindow& emu_window, Frontend::EmuWindow* secondary_window,
          Core::System& system) {
    g_memory = &system.Memory();
    Pica::Init();

    if (emu_window.ShouldDeferRendererInit()) {
        // We will come back to it later
        return;
    }
    g_renderer = std::make_unique<SwRenderer::RendererSoftware>(system, emu_window);
}

/// Shutdown the video core
void Shutdown() {
    Pica::Shutdown();
    g_renderer.reset();

    LOG_DEBUG(Render, "shutdown OK");
}

template <class Archive>
void serialize(Archive& ar, const unsigned int) {
    ar& Pica::g_state;
}

} // namespace VideoCore

SERIALIZE_IMPL(VideoCore)
