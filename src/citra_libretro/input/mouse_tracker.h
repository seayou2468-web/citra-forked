// Copyright 2017 Citra Emulator Project
// Licensed under GPLv2 or any later version
// Refer to the license.txt file included.

#pragma once

#include "common/math_util.h"

namespace LibRetro {

namespace Input {

class MouseTracker {
public:
    MouseTracker() = default;
    ~MouseTracker() = default;

    void OnMouseMove(int xDelta, int yDelta) {}
    void Restrict(int minX, int minY, int maxX, int maxY) {}
    void Update(int bufferWidth, int bufferHeight, Common::Rectangle<unsigned> bottomScreen) {}
    void Render(int bufferWidth, int bufferHeight) {}

    bool IsPressed() { return false; }
    std::pair<unsigned, unsigned> GetPressedPosition() { return {0, 0}; }
};

} // namespace Input

} // namespace LibRetro
