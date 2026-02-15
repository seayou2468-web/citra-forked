import sys

with open("src/video_core/renderer_software/sw_rasterizer.cpp", "r") as f:
    content = f.read()

# Replace the slow interpolation lambda with a faster one using floats
slow_lambda = """                const auto get_interpolated_attribute = [&](f24 attr0, f24 attr1, f24 attr2) {
                    auto attr_over_w = Common::MakeVec(attr0, attr1, attr2);
                    f24 interpolated_attr_over_w =
                        Common::Dot(attr_over_w, baricentric_coordinates);
                    return interpolated_attr_over_w * interpolated_w_inverse;
                };"""

fast_lambda = """                const float b0 = static_cast<float>(w0);
                const float b1 = static_cast<float>(w1);
                const float b2 = static_cast<float>(w2);
                const float inv_wsum = 1.0f / static_cast<float>(wsum);
                const float inv_w_val = interpolated_w_inverse.ToFloat32();

                auto get_interpolated_attribute_fast = [&](float a0, float a1, float a2) {
                    return (a0 * b0 + a1 * b1 + a2 * b2) * inv_w_val * inv_wsum;
                };"""

content = content.replace(slow_lambda, fast_lambda)

# Now replace usages of get_interpolated_attribute with get_interpolated_attribute_fast
# and ensure they pass .ToFloat32() or use the raw values.

# This is a bit complex for a simple string replace, but let's try to match the patterns.
content = content.replace("get_interpolated_attribute(v0.color.r(), v1.color.r(), v2.color.r()).ToFloat32()",
                          "get_interpolated_attribute_fast(v0.color.r().ToFloat32(), v1.color.r().ToFloat32(), v2.color.r().ToFloat32())")
content = content.replace("get_interpolated_attribute(v0.color.g(), v1.color.g(), v2.color.g()).ToFloat32()",
                          "get_interpolated_attribute_fast(v0.color.g().ToFloat32(), v1.color.g().ToFloat32(), v2.color.g().ToFloat32())")
content = content.replace("get_interpolated_attribute(v0.color.b(), v1.color.b(), v2.color.b()).ToFloat32()",
                          "get_interpolated_attribute_fast(v0.color.b().ToFloat32(), v1.color.b().ToFloat32(), v2.color.b().ToFloat32())")
content = content.replace("get_interpolated_attribute(v0.color.a(), v1.color.a(), v2.color.a()).ToFloat32()",
                          "get_interpolated_attribute_fast(v0.color.a().ToFloat32(), v1.color.a().ToFloat32(), v2.color.a().ToFloat32())")

# For UVs
content = content.replace("uv[0].u() = get_interpolated_attribute(v0.tc0.u(), v1.tc0.u(), v2.tc0.u());",
                          "uv[0].u() = f24::FromFloat32(get_interpolated_attribute_fast(v0.tc0.u().ToFloat32(), v1.tc0.u().ToFloat32(), v2.tc0.u().ToFloat32()));")
content = content.replace("uv[0].v() = get_interpolated_attribute(v0.tc0.v(), v1.tc0.v(), v2.tc0.v());",
                          "uv[0].v() = f24::FromFloat32(get_interpolated_attribute_fast(v0.tc0.v().ToFloat32(), v1.tc0.v().ToFloat32(), v2.tc0.v().ToFloat32()));")
content = content.replace("uv[1].u() = get_interpolated_attribute(v0.tc1.u(), v1.tc1.u(), v2.tc1.u());",
                          "uv[1].u() = f24::FromFloat32(get_interpolated_attribute_fast(v0.tc1.u().ToFloat32(), v1.tc1.u().ToFloat32(), v2.tc1.u().ToFloat32()));")
content = content.replace("uv[1].v() = get_interpolated_attribute(v0.tc1.v(), v1.tc1.v(), v2.tc1.v());",
                          "uv[1].v() = f24::FromFloat32(get_interpolated_attribute_fast(v0.tc1.v().ToFloat32(), v1.tc1.v().ToFloat32(), v2.tc1.v().ToFloat32()));")
content = content.replace("uv[2].u() = get_interpolated_attribute(v0.tc2.u(), v1.tc2.u(), v2.tc2.u());",
                          "uv[2].u() = f24::FromFloat32(get_interpolated_attribute_fast(v0.tc2.u().ToFloat32(), v1.tc2.u().ToFloat32(), v2.tc2.u().ToFloat32()));")
content = content.replace("uv[2].v() = get_interpolated_attribute(v0.tc2.v(), v1.tc2.v(), v2.tc2.v());",
                          "uv[2].v() = f24::FromFloat32(get_interpolated_attribute_fast(v0.tc2.v().ToFloat32(), v1.tc2.v().ToFloat32(), v2.tc2.v().ToFloat32()));")

with open("src/video_core/renderer_software/sw_rasterizer.cpp", "w") as f:
    f.write(content)
