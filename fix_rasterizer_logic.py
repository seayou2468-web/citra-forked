import sys
import re

with open("src/video_core/renderer_software/sw_rasterizer.cpp", "r") as f:
    content = f.read()

# Fix the fast_lambda and the interp_w_inv calculation
old_block = re.search(r"const auto baricentric_coordinates =.*?const f24 interpolated_w_inverse =.*?const float inv_w_val = interpolated_w_inverse.ToFloat32\(\);.*?auto get_interpolated_attribute_fast = \[&\]\(float a0, float a1, float a2\) \{.*?return \(a0 \* b0 \+ a1 \* b1 \+ a2 \* b2\) \* inv_w_val \* inv_wsum;.*?};", content, re.DOTALL)

if old_block:
    new_block = """                const float fw0 = static_cast<float>(w0);
                const float fw1 = static_cast<float>(w1);
                const float fw2 = static_cast<float>(w2);

                const float interp_w_inv = 1.0f / (v0.pos.w.ToFloat32() * fw0 + v1.pos.w.ToFloat32() * fw1 + v2.pos.w.ToFloat32() * fw2);

                auto get_interpolated_attribute_fast = [&](float a0, float a1, float a2) {
                    return (a0 * fw0 + a1 * fw1 + a2 * fw2) * interp_w_inv;
                };"""
    content = content.replace(old_block.group(0), new_block)

# Also need to fix where interpolated_w_inverse was used elsewhere (e.g. for depth or texture coordinate 0)
# Actually, let's just make interpolated_w_inverse a float wrapper for compatibility if needed,
# but it's better to just use the float.

with open("src/video_core/renderer_software/sw_rasterizer.cpp", "w") as f:
    f.write(content)
