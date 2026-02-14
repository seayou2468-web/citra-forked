import re

with open('src/video_core/renderer_software/sw_framebuffer.cpp', 'r') as f:
    content = f.read()

# Add dirty checks for other formats
rgb8_fix = r'''    case Pica::FramebufferRegs::ColorFormat::RGB8: {
        u8 temp[3];
        Common::Color::EncodeRGB8(color, temp);
        if (__builtin_expect(std::memcmp(dst_pixel, temp, 3) != 0, 1)) {
            std::memcpy(dst_pixel, temp, 3);
        }
        break;
    }'''

rgb565_fix = r'''    case Pica::FramebufferRegs::ColorFormat::RGB565: {
        u16 old_val;
        std::memcpy(&old_val, dst_pixel, 2);
        u8 temp[2];
        Common::Color::EncodeRGB565(color, temp);
        u16 new_val;
        std::memcpy(&new_val, temp, 2);
        if (__builtin_expect(old_val != new_val, 1)) {
            std::memcpy(dst_pixel, &new_val, 2);
        }
        break;
    }'''

content = re.sub(r'case Pica::FramebufferRegs::ColorFormat::RGB8:.*?break;', rgb8_fix, content, flags=re.DOTALL)
content = re.sub(r'case Pica::FramebufferRegs::ColorFormat::RGB565:.*?break;', rgb565_fix, content, flags=re.DOTALL)

with open('src/video_core/renderer_software/sw_framebuffer.cpp', 'w') as f:
    f.write(content)
