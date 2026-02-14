// Copyright 2015 Citra Emulator Project
// Licensed under GPLv2 or any later version
// Refer to the license.txt file included.

#include <cmath>
#include <cstring>
#include "common/arch.h"
#include "common/assert.h"
#include "common/bit_set.h"
#include "common/logging/log.h"
#include "common/microprofile.h"
#include "video_core/regs_rasterizer.h"
#include "video_core/regs_shader.h"
#include "video_core/shader/shader.h"
#include "video_core/shader/shader_interpreter.h"
#include "video_core/shader/shader_jit.h"
#include "video_core/video_core.h"

namespace Pica::Shader {

void OutputVertex::ValidateSemantics(const RasterizerRegs& regs) {
    u32 num_attributes = regs.vs_output_total;
    ASSERT(num_attributes <= 7);
    for (std::size_t attrib = 0; attrib < num_attributes; ++attrib) {
        u32 output_register_map = regs.vs_output_attributes[attrib].raw;
        for (std::size_t comp = 0; comp < 4; ++comp) {
            u32 semantic = (output_register_map >> (8 * comp)) & 0x1F;
            ASSERT_MSG(semantic < 24 || semantic == RasterizerRegs::VSOutputAttributes::INVALID,
                       "Invalid/unknown semantic id: {}", semantic);
        }
    }
}

OutputVertex OutputVertex::FromAttributeBuffer(const RasterizerRegs& regs,
                                               const AttributeBuffer& input) {
    union {
        OutputVertex ret{};
        std::array<f24, 32> vertex_slots_overflow;
    };
    vertex_slots_overflow.fill(f24::One());
    static_assert(sizeof(std::array<f24, 24>) == sizeof(ret),
                  "Struct and array have different sizes.");
    u32 num_attributes = regs.vs_output_total & 7;
    for (std::size_t attrib = 0; attrib < num_attributes; ++attrib) {
        const auto output_register_map = regs.vs_output_attributes[attrib];
        vertex_slots_overflow[output_register_map.map_x] = input.attr[attrib][0];
        vertex_slots_overflow[output_register_map.map_y] = input.attr[attrib][1];
        vertex_slots_overflow[output_register_map.map_z] = input.attr[attrib][2];
        vertex_slots_overflow[output_register_map.map_w] = input.attr[attrib][3];
    }
    for (u32 i = 0; i < 4; ++i) {
        float c = std::fabs(ret.color[i].ToFloat32());
        ret.color[i] = f24::FromFloat32(c < 1.0f ? c : 1.0f);
    }
    return ret;
}

void UnitState::LoadInput(const ShaderRegs& config, const AttributeBuffer& input) {
    const u32 max_attribute = config.max_input_attribute_index;
    for (u32 attr = 0; attr <= max_attribute; ++attr) {
        u32 reg = config.GetRegisterForAttribute(attr);
        registers.input[reg] = input.attr[attr];
    }
}

static void CopyRegistersToOutput(std::span<Common::Vec4<f24>, 16> regs, u32 mask,
                                  AttributeBuffer& buffer) {
    int output_i = 0;
    for (int reg : Common::BitSet<u32>(mask)) {
        buffer.attr[output_i++] = regs[reg];
    }
}

void UnitState::WriteOutput(const ShaderRegs& config, AttributeBuffer& output) {
    CopyRegistersToOutput(registers.output, config.output_mask, output);
}

UnitState::UnitState(GSEmitter* emitter) : emitter_ptr(emitter) {}

GSEmitter::GSEmitter() {
    handlers = new Handlers;
}

GSEmitter::~GSEmitter() {
    delete handlers;
}

void GSEmitter::Emit(std::span<Common::Vec4<f24>, 16> output_regs) {
    ASSERT(vertex_id < 3);
    CopyRegistersToOutput(output_regs, output_mask, buffer[vertex_id]);
    if (prim_emit) {
        if (winding)
            handlers->winding_setter();
        for (std::size_t i = 0; i < buffer.size(); ++i) {
            handlers->vertex_handler(buffer[i]);
        }
    }
}

GSUnitState::GSUnitState() : UnitState(&emitter) {}

void GSUnitState::SetVertexHandler(VertexHandler vertex_handler, WindingSetter winding_setter) {
    emitter.handlers->vertex_handler = std::move(vertex_handler);
    emitter.handlers->winding_setter = std::move(winding_setter);
}

void GSUnitState::ConfigOutput(const ShaderRegs& config) {
    emitter.output_mask = config.output_mask;
}

MICROPROFILE_DEFINE(GPU_Shader, "GPU", "Shader", MP_RGB(50, 50, 240));

#if (CITRA_ARCH(x86_64) || CITRA_ARCH(arm64)) && !defined(CITRA_FORCE_INTERPRETER)
static std::unique_ptr<JitEngine> jit_engine;
#endif
static InterpreterEngine interpreter_engine;

ShaderEngine* GetEngine() {
#if (CITRA_ARCH(x86_64) || CITRA_ARCH(arm64)) && !defined(CITRA_FORCE_INTERPRETER)
    if (VideoCore::g_shader_jit_enabled) {
        if (jit_engine == nullptr) {
            jit_engine = std::make_unique<JitEngine>();
        }
        return jit_engine.get();
    }
#endif
    return &interpreter_engine;
}

void Shutdown() {
#if (CITRA_ARCH(x86_64) || CITRA_ARCH(arm64)) && !defined(CITRA_FORCE_INTERPRETER)
    jit_engine.reset();
#endif
}

} // namespace Pica::Shader

#if !((CITRA_ARCH(x86_64) || CITRA_ARCH(arm64)) && !defined(CITRA_FORCE_INTERPRETER))
namespace Pica::Shader {
JitEngine::JitEngine() = default;
JitEngine::~JitEngine() = default;
void JitEngine::SetupBatch(ShaderSetup& setup, u32 entry_point) {}
void JitEngine::Run(const ShaderSetup& setup, UnitState& state) const {}
void JitEngine::ClearCache() {}
}
#endif
