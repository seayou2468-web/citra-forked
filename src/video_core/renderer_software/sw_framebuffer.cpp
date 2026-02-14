// Copyright 2017 Citra Emulator Project
// Licensed under GPLv2 or any later version
// Refer to the license.txt file included.

#include <algorithm>
#include <cstring>
#include "common/color.h"
#include "common/logging/log.h"
#include "common/math_util.h"
#include "core/memory.h"
#include "video_core/pica_types.h"
#include "video_core/renderer_software/sw_framebuffer.h"
#include "video_core/utils.h"

namespace SwRenderer {

Framebuffer::Framebuffer(Memory::MemorySystem& memory, const Pica::FramebufferRegs& regs)
    : memory(memory), regs(regs) {}

Framebuffer::~Framebuffer() = default;

void Framebuffer::Bind() {
    const auto& framebuffer = regs.framebuffer;
    const PAddr addr = framebuffer.GetColorBufferPhysicalAddress();
    if (color_addr != addr) [[unlikely]] {
        color_addr = addr;
        color_buffer = memory.GetPhysicalPointer(color_addr);
    }
    const PAddr depth_addr_new = regs.framebuffer.GetDepthBufferPhysicalAddress();
    if (depth_addr != depth_addr_new) [[unlikely]] {
        depth_addr = depth_addr_new;
        depth_buffer = memory.GetPhysicalPointer(depth_addr);
    }
}

void Framebuffer::DrawPixel(u32 x, u32 y, const Common::Vec4<u8>& color) const {
    const auto& framebuffer = regs.framebuffer;
    y = framebuffer.height - y;

    const u32 coarse_y = y & ~7;
    const u32 bytes_per_pixel = Pica::FramebufferRegs::BytesPerColorPixel(framebuffer.color_format);
    const u32 dst_offset = VideoCore::GetMortonOffset(x, y, bytes_per_pixel) +
                           coarse_y * framebuffer.width * bytes_per_pixel;
    u8* dst_pixel = color_buffer + dst_offset;

    switch (framebuffer.color_format) {
    case Pica::FramebufferRegs::ColorFormat::RGBA8: {
        u32 old_val;
        std::memcpy(&old_val, dst_pixel, 4);
        u8 temp[4];
        Common::Color::EncodeRGBA8(color, temp);
        u32 new_val;
        std::memcpy(&new_val, temp, 4);
        if (__builtin_expect(old_val != new_val, 1)) {
            std::memcpy(dst_pixel, &new_val, 4);
        }
        break;
    }
    case Pica::FramebufferRegs::ColorFormat::RGB8:
        Common::Color::EncodeRGB8(color, dst_pixel);
        break;
    case Pica::FramebufferRegs::ColorFormat::RGB5A1:
        Common::Color::EncodeRGB5A1(color, dst_pixel);
        break;
    case Pica::FramebufferRegs::ColorFormat::RGB565:
        Common::Color::EncodeRGB565(color, dst_pixel);
        break;
    case Pica::FramebufferRegs::ColorFormat::RGBA4:
        Common::Color::EncodeRGBA4(color, dst_pixel);
        break;
    default:
        LOG_CRITICAL(Render_Software, "Unknown framebuffer color format {:x}",
                     static_cast<u32>(framebuffer.color_format.Value()));
        UNIMPLEMENTED();
    }
}

const Common::Vec4<u8> Framebuffer::GetPixel(u32 x, u32 y) const {
    const auto& framebuffer = regs.framebuffer;
    y = framebuffer.height - y;

    const u32 coarse_y = y & ~7;
    const u32 bytes_per_pixel = Pica::FramebufferRegs::BytesPerColorPixel(framebuffer.color_format);
    const u32 src_offset = VideoCore::GetMortonOffset(x, y, bytes_per_pixel) +
                           coarse_y * framebuffer.width * bytes_per_pixel;
    const u8* src_pixel = color_buffer + src_offset;

    switch (framebuffer.color_format) {
    case Pica::FramebufferRegs::ColorFormat::RGBA8:
        return Common::Color::DecodeRGBA8(src_pixel);
    case Pica::FramebufferRegs::ColorFormat::RGB8:
        return Common::Color::DecodeRGB8(src_pixel);
    case Pica::FramebufferRegs::ColorFormat::RGB5A1:
        return Common::Color::DecodeRGB5A1(src_pixel);
    case Pica::FramebufferRegs::ColorFormat::RGB565:
        return Common::Color::DecodeRGB565(src_pixel);
    case Pica::FramebufferRegs::ColorFormat::RGBA4:
        return Common::Color::DecodeRGBA4(src_pixel);
    default:
        LOG_CRITICAL(Render_Software, "Unknown framebuffer color format {:x}",
                     static_cast<u32>(framebuffer.color_format.Value()));
        UNIMPLEMENTED();
    }

    return {0, 0, 0, 0};
}

u32 Framebuffer::GetDepth(u32 x, u32 y) const {
    const auto& framebuffer = regs.framebuffer;
    y = framebuffer.height - y;

    const u32 coarse_y = y & ~7;
    const u32 bytes_per_pixel = Pica::FramebufferRegs::BytesPerDepthPixel(framebuffer.depth_format);
    const u32 stride = framebuffer.width * bytes_per_pixel;

    const u32 src_offset = VideoCore::GetMortonOffset(x, y, bytes_per_pixel) + coarse_y * stride;
    const u8* src_pixel = depth_buffer + src_offset;

    switch (framebuffer.depth_format) {
    case Pica::FramebufferRegs::DepthFormat::D16:
        return Common::Color::DecodeD16(src_pixel);
    case Pica::FramebufferRegs::DepthFormat::D24:
        return Common::Color::DecodeD24(src_pixel);
    case Pica::FramebufferRegs::DepthFormat::D24S8:
        return Common::Color::DecodeD24S8(src_pixel).x;
    default:
        LOG_CRITICAL(HW_GPU, "Unimplemented depth format {}",
                     static_cast<u32>(framebuffer.depth_format.Value()));
        UNIMPLEMENTED();
        return 0;
    }
}

u8 Framebuffer::GetStencil(u32 x, u32 y) const {
    const auto& framebuffer = regs.framebuffer;
    y = framebuffer.height - y;

    const u32 coarse_y = y & ~7;
    const u32 bytes_per_pixel = Pica::FramebufferRegs::BytesPerDepthPixel(framebuffer.depth_format);
    const u32 stride = framebuffer.width * bytes_per_pixel;

    const u32 src_offset = VideoCore::GetMortonOffset(x, y, bytes_per_pixel) + coarse_y * stride;
    const u8* src_pixel = depth_buffer + src_offset;

    switch (framebuffer.depth_format) {
    case Pica::FramebufferRegs::DepthFormat::D24S8:
        return Common::Color::DecodeD24S8(src_pixel).y;
    default:
        return 0;
    }
}

void Framebuffer::SetDepth(u32 x, u32 y, u32 value) const {
    const auto& framebuffer = regs.framebuffer;
    y = framebuffer.height - y;

    const u32 coarse_y = y & ~7;
    const u32 bytes_per_pixel = Pica::FramebufferRegs::BytesPerDepthPixel(framebuffer.depth_format);
    const u32 stride = framebuffer.width * bytes_per_pixel;

    const u32 dst_offset = VideoCore::GetMortonOffset(x, y, bytes_per_pixel) + coarse_y * stride;
    u8* dst_pixel = depth_buffer + dst_offset;

    switch (framebuffer.depth_format) {
    case Pica::FramebufferRegs::DepthFormat::D16:
        Common::Color::EncodeD16(value, dst_pixel);
        break;
    case Pica::FramebufferRegs::DepthFormat::D24:
        Common::Color::EncodeD24(value, dst_pixel);
        break;
    case Pica::FramebufferRegs::DepthFormat::D24S8:
        Common::Color::EncodeD24X8(value, dst_pixel);
        break;
    default:
        LOG_CRITICAL(HW_GPU, "Unimplemented depth format {}",
                     static_cast<u32>(framebuffer.depth_format.Value()));
        UNIMPLEMENTED();
        break;
    }
}

void Framebuffer::SetStencil(u32 x, u32 y, u8 value) const {
    const auto& framebuffer = regs.framebuffer;
    y = framebuffer.height - y;

    const u32 coarse_y = y & ~7;
    const u32 bytes_per_pixel = Pica::FramebufferRegs::BytesPerDepthPixel(framebuffer.depth_format);
    const u32 stride = framebuffer.width * bytes_per_pixel;

    const u32 dst_offset = VideoCore::GetMortonOffset(x, y, bytes_per_pixel) + coarse_y * stride;
    u8* dst_pixel = depth_buffer + dst_offset;

    switch (framebuffer.depth_format) {
    case Pica::FramebufferRegs::DepthFormat::D16:
    case Pica::FramebufferRegs::DepthFormat::D24:
        // Nothing to do
        break;
    case Pica::FramebufferRegs::DepthFormat::D24S8:
        Common::Color::EncodeX24S8(value, dst_pixel);
        break;
    default:
        LOG_CRITICAL(HW_GPU, "Unimplemented depth format {}",
                     static_cast<u32>(framebuffer.depth_format.Value()));
        UNIMPLEMENTED();
        break;
    }
}

void Framebuffer::DrawShadowMapPixel(u32 x, u32 y, u32 depth, u8 stencil) const {
    const auto& framebuffer = regs.framebuffer;
    const auto& shadow = regs.shadow;
    const PAddr addr = framebuffer.GetColorBufferPhysicalAddress();

    y = framebuffer.height - y;

    const u32 coarse_y = y & ~7;
    u32 bytes_per_pixel = 4;
    u32 dst_offset = VideoCore::GetMortonOffset(x, y, bytes_per_pixel) +
                     coarse_y * framebuffer.width * bytes_per_pixel;
    u8* shadow_buffer = memory.GetPhysicalPointer(addr);
    u8* dst_pixel = shadow_buffer + dst_offset;

    const auto ref = Common::Color::DecodeD24S8(dst_pixel);
    const u32 ref_z = ref.x;
    const u32 ref_s = ref.y;

    if (depth >= ref_z) {
        return;
    }

    if (stencil == 0) {
        Common::Color::EncodeD24X8(depth, dst_pixel);
    } else {
        const Pica::f16 constant = Pica::f16::FromRaw(shadow.constant);
        const Pica::f16 linear = Pica::f16::FromRaw(shadow.linear);
        const Pica::f16 x_ = Pica::f16::FromFloat32(static_cast<float>(depth) / ref_z);
        const Pica::f16 stencil_new = Pica::f16::FromFloat32(stencil) / (constant + linear * x_);
        stencil = static_cast<u8>(std::clamp(stencil_new.ToFloat32(), 0.0f, 255.0f));

        if (stencil < ref_s) {
            Common::Color::EncodeX24S8(stencil, dst_pixel);
        }
    }
}

u8 PerformStencilAction(Pica::FramebufferRegs::StencilAction action, u8 old_stencil, u8 ref) {
    switch (action) {
    case Pica::FramebufferRegs::StencilAction::Keep:
        return old_stencil;
    case Pica::FramebufferRegs::StencilAction::Zero:
        return 0;
    case Pica::FramebufferRegs::StencilAction::Replace:
        return ref;
    case Pica::FramebufferRegs::StencilAction::Increment:
        return std::min<u8>(old_stencil, 254) + 1;
    case Pica::FramebufferRegs::StencilAction::Decrement:
        return std::max<u8>(old_stencil, 1) - 1;
    case Pica::FramebufferRegs::StencilAction::Invert:
        return ~old_stencil;
    case Pica::FramebufferRegs::StencilAction::IncrementWrap:
        return old_stencil + 1;
    case Pica::FramebufferRegs::StencilAction::DecrementWrap:
        return old_stencil - 1;
    default:
        UNIMPLEMENTED();
        return 0;
    }
}

Common::Vec4<u8> EvaluateBlendEquation(const Common::Vec4<u8>& src,
                                       const Common::Vec4<u8>& srcfactor,
                                       const Common::Vec4<u8>& dest,
                                       const Common::Vec4<u8>& destfactor,
                                       Pica::FramebufferRegs::BlendEquation equation) {
    Common::Vec4<int> result;

    const auto src_result = (src.Cast<int>() * srcfactor.Cast<int>());
    const auto dst_result = (dest.Cast<int>() * destfactor.Cast<int>());

    switch (equation) {
    case Pica::FramebufferRegs::BlendEquation::Add:
        result = (src_result + dst_result) / 255;
        break;
    case Pica::FramebufferRegs::BlendEquation::Subtract:
        result = (src_result - dst_result) / 255;
        break;
    case Pica::FramebufferRegs::BlendEquation::ReverseSubtract:
        result = (dst_result - src_result) / 255;
        break;
    case Pica::FramebufferRegs::BlendEquation::Min:
        result.x = std::min(src_result.x, dst_result.x) / 255;
        result.y = std::min(src_result.y, dst_result.y) / 255;
        result.z = std::min(src_result.z, dst_result.z) / 255;
        result.w = std::min(src_result.w, dst_result.w) / 255;
        break;
    case Pica::FramebufferRegs::BlendEquation::Max:
        result.x = std::max(src_result.x, dst_result.x) / 255;
        result.y = std::max(src_result.y, dst_result.y) / 255;
        result.z = std::max(src_result.z, dst_result.z) / 255;
        result.w = std::max(src_result.w, dst_result.w) / 255;
        break;
    default:
        UNIMPLEMENTED();
    }

    return Common::Vec4<u8>(static_cast<u8>(std::clamp(result.x, 0, 255)),
                            static_cast<u8>(std::clamp(result.y, 0, 255)),
                            static_cast<u8>(std::clamp(result.z, 0, 255)),
                            static_cast<u8>(std::clamp(result.w, 0, 255)));
};

u8 LogicOp(u8 src, u8 dest, Pica::FramebufferRegs::LogicOp op) {
    switch (op) {
    case Pica::FramebufferRegs::LogicOp::Clear:
        return 0;
    case Pica::FramebufferRegs::LogicOp::And:
        return src & dest;
    case Pica::FramebufferRegs::LogicOp::AndReverse:
        return src & ~dest;
    case Pica::FramebufferRegs::LogicOp::Copy:
        return src;
    case Pica::FramebufferRegs::LogicOp::Set:
        return 255;
    case Pica::FramebufferRegs::LogicOp::CopyInverted:
        return ~src;
    case Pica::FramebufferRegs::LogicOp::NoOp:
        return dest;
    case Pica::FramebufferRegs::LogicOp::Invert:
        return ~dest;
    case Pica::FramebufferRegs::LogicOp::Nand:
        return ~(src & dest);
    case Pica::FramebufferRegs::LogicOp::Or:
        return src | dest;
    case Pica::FramebufferRegs::LogicOp::Nor:
        return ~(src | dest);
    case Pica::FramebufferRegs::LogicOp::Xor:
        return src ^ dest;
    case Pica::FramebufferRegs::LogicOp::Equiv:
        return ~(src ^ dest);
    case Pica::FramebufferRegs::LogicOp::AndInverted:
        return ~src & dest;
    case Pica::FramebufferRegs::LogicOp::OrReverse:
        return src | ~dest;
    case Pica::FramebufferRegs::LogicOp::OrInverted:
        return ~src | dest;
    }
    return dest;
};

} // namespace SwRenderer
