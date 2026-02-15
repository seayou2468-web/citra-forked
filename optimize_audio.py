import sys

with open("src/audio_core/libretro_sink.h", "r") as f:
    header = f.read()

# Add a persistent buffer to Impl
if "struct Impl;" in header:
    # We need to see the actual class definition
    pass

with open("src/audio_core/libretro_sink.cpp", "r") as f:
    content = f.read()

# Update Impl definition
content = content.replace("    std::function<void(s16*, std::size_t)> cb;",
                          "    std::function<void(s16*, std::size_t)> cb;\n    std::vector<s16> buffer;")

# Update OnAudioSubmission
old_sub = """void LibRetroSink::OnAudioSubmission(std::size_t frames) {
    std::vector<s16> buffer(frames * 2);

    this->impl->cb(buffer.data(), buffer.size() / 2);

    LibRetro::SubmitAudio(buffer.data(), buffer.size() / 2);
}"""

new_sub = """void LibRetroSink::OnAudioSubmission(std::size_t frames) {
    if (this->impl->buffer.size() < frames * 2) {
        this->impl->buffer.resize(frames * 2);
    }

    this->impl->cb(this->impl->buffer.data(), frames);

    LibRetro::SubmitAudio(this->impl->buffer.data(), frames);
}"""

content = content.replace(old_sub, new_sub)

with open("src/audio_core/libretro_sink.cpp", "w") as f:
    f.write(content)
