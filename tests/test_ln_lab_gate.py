"""Execute the actual C++ gate shipped by the lab patch, including negative GPUs."""
import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class LabGateTests(unittest.TestCase):
    def test_exact_gpu_and_application_gate(self):
        with tempfile.TemporaryDirectory() as folder:
            subprocess.run([
                "git", "apply", "--include=src/freedreno/vulkan/tu_amaral_lab.h",
                str(ROOT / "patches/0009-lab-a740-profiled-autotune.patch"),
            ], cwd=folder, check=True)
            test = pathlib.Path(folder) / "gate.cpp"
            test.write_text(r'''
#include "src/freedreno/vulkan/tu_amaral_lab.h"
#include <cassert>
int main() {
  const char *eden = "yuzu Emulator";
  assert(amaral_a740_eden_lab_matches(740, 0, eden, eden));
  assert(amaral_a740_eden_lab_matches(0, 0x43050a01ULL, eden, eden));
  assert(amaral_a740_eden_lab_matches(0, 0xffff43050a01ULL, eden, eden));
  assert(amaral_a740_eden_lab_matches(740, 0x43050a01ULL, eden, eden));
  for (auto gpu : {630, 650, 660, 710, 720, 730, 750, 810, 825, 830, 840})
    assert(!amaral_a740_eden_lab_matches(gpu, 0, eden, eden));
  assert(!amaral_a740_eden_lab_matches(0, 0xffff43050c01ULL, eden, eden));
  assert(!amaral_a740_eden_lab_matches(750, 0x43050a01ULL, eden, eden));
  assert(!amaral_a740_eden_lab_matches(740, 0x44030000ULL, eden, eden));
  assert(!amaral_a740_eden_lab_matches(0, 0, eden, eden));
  assert(!amaral_a740_eden_lab_matches(740, 0, nullptr, eden));
  assert(!amaral_a740_eden_lab_matches(740, 0, eden, nullptr));
  assert(!amaral_a740_eden_lab_matches(740, 0, "Cemu", eden));
  assert(!amaral_a740_eden_lab_matches(740, 0, eden, "DXVK"));
  assert(!amaral_a740_eden_lab_matches(740, 0, "yuzu Emulator-other", eden));
}
''')
            binary = pathlib.Path(folder) / "gate"
            subprocess.run(["c++", "-std=c++17", "-Wall", "-Wextra", "-Werror",
                            str(test), "-o", str(binary)], check=True)
            subprocess.run([str(binary)], check=True)
