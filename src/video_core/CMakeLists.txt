

add_library(video_core STATIC
    command_processor.cpp
    command_processor.h
    custom_textures/custom_format.cpp
    custom_textures/custom_format.h
    custom_textures/custom_tex_manager.cpp
    custom_textures/custom_tex_manager.h
    custom_textures/material.cpp
    custom_textures/material.h
    debug_utils/debug_utils.cpp
    debug_utils/debug_utils.h
    geometry_pipeline.cpp
    geometry_pipeline.h
    gpu_debugger.h
    pica.cpp
    pica.h
    pica_state.h
    pica_types.h
    precompiled_headers.h
    primitive_assembly.cpp
    primitive_assembly.h
    rasterizer_interface.h
    regs.cpp
    regs.h
    regs_framebuffer.h
    regs_lighting.h
    regs_pipeline.h
    regs_rasterizer.h
    regs_shader.h
    regs_texturing.h
    renderer_base.cpp
    renderer_base.h
    rasterizer_cache/framebuffer_base.h
    rasterizer_cache/pixel_format.cpp
    rasterizer_cache/pixel_format.h
    rasterizer_cache/rasterizer_cache.cpp
    rasterizer_cache/rasterizer_cache.h
    rasterizer_cache/rasterizer_cache_base.h
    rasterizer_cache/sampler_params.h
    rasterizer_cache/slot_id.h
    rasterizer_cache/surface_base.cpp
    rasterizer_cache/surface_base.h
    rasterizer_cache/surface_params.cpp
    rasterizer_cache/surface_params.h
    rasterizer_cache/texture_codec.h
    rasterizer_cache/texture_cube.h
    rasterizer_cache/utils.cpp
    rasterizer_cache/utils.h
    renderer_software/renderer_software.cpp
    renderer_software/renderer_software.h
    renderer_software/sw_clipper.cpp
    renderer_software/sw_clipper.h
    renderer_software/sw_framebuffer.cpp
    renderer_software/sw_framebuffer.h
    renderer_software/sw_lighting.cpp
    renderer_software/sw_lighting.h
    renderer_software/sw_proctex.cpp
    renderer_software/sw_proctex.h
    renderer_software/sw_rasterizer.cpp
    renderer_software/sw_rasterizer.h
    renderer_software/sw_texturing.cpp
    renderer_software/sw_texturing.h
    shader/debug_data.h
    shader/shader.cpp
    shader/shader.h
    shader/shader_interpreter.cpp
    shader/shader_interpreter.h
    texture/etc1.cpp
    texture/etc1.h
    texture/texture_decode.cpp
    texture/texture_decode.h
    utils.h
    vertex_loader.cpp
    vertex_loader.h
    video_core.cpp
    video_core.h
)





if ("x86_64" IN_LIST ARCHITECTURE)
    target_sources(video_core PRIVATE
        shader/shader_jit.cpp
        shader/shader_jit.h
        shader/shader_jit_x64_compiler.cpp
        shader/shader_jit_x64_compiler.h
    )
endif()

if ("arm64" IN_LIST ARCHITECTURE)
    target_sources(video_core PRIVATE
        shader/shader_jit.cpp
        shader/shader_jit.h
        shader/shader_jit_a64_compiler.cpp
        shader/shader_jit_a64_compiler.h
    )
endif()

create_target_directory_groups(video_core)

target_link_libraries(video_core PUBLIC citra_common citra_core)
target_link_libraries(video_core PRIVATE Boost::serialization dds-ktx json-headers nihstro-headers tsl::robin_map)
target_link_libraries(video_core PRIVATE )

if ("x86_64" IN_LIST ARCHITECTURE)
    target_link_libraries(video_core PUBLIC xbyak)
endif()

if ("arm64" IN_LIST ARCHITECTURE)
    target_link_libraries(video_core PUBLIC oaknut)
endif()

if (CITRA_USE_PRECOMPILED_HEADERS)
    target_precompile_headers(video_core PRIVATE precompiled_headers.h)
endif()
