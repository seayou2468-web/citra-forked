import sys

content = open("src/citra_libretro/citra_libretro.cpp", "r").read()

# Find the start of retro_run
start_run = content.find("void retro_run()")
# Find the start of context_reset
start_context = content.find("void context_reset()")

if start_run != -1 and start_context != -1:
    before_run = content[:start_run]
    run_body = content[start_run:start_context]
    after_context = content[start_context:]

    # We want to keep until the end of the for loop and the comments
    end_of_loop = run_body.rfind("break; // Return after 16ms to keep frontend responsive")
    if end_of_loop != -1:
        # Find the closing brace of the for loop
        loop_close = run_body.find("}", end_of_loop)
        # Find the comments after the loop
        comment_end = run_body.find("// or handled by the emu_window.", loop_close)
        if comment_end != -1:
            actual_end = run_body.find("\n", comment_end)
            new_run_body = run_body[:actual_end+1] + "\n}\n"
            content = before_run + new_run_body + after_context

# Also remove SwapBuffers in retro_load_game
content = content.replace("emu_instance->emu_window->SwapBuffers();", "// emu_instance->emu_window->SwapBuffers();")

with open("src/citra_libretro/citra_libretro.cpp", "w") as f:
    f.write(content)
