import sys

with open("src/citra_libretro/citra_libretro.cpp", "r") as f:
    content = f.read()

# Disable telemetry and set default log level to Info
if "void UpdateSettings()" in content:
    content = content.replace("void UpdateSettings() {",
                              "void UpdateSettings() {\n    Settings::values.enable_telemetry = false;\n    Settings::values.log_filter = \"*:Info\";")

with open("src/citra_libretro/citra_libretro.cpp", "w") as f:
    f.write(content)
