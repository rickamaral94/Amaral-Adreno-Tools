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
                "git", "apply", "--include=src/freedreno/vulkan/tu_amaral_readback_lab.h",
                str(ROOT / "patches/0010-lab-a740-readback-counters.patch"),
            ], cwd=folder, check=True)
            test = pathlib.Path(folder) / "gate.cpp"
            test.write_text(r'''
#include "src/freedreno/vulkan/tu_amaral_readback_lab.h"
#include <cassert>
int main() {
  amaral_readback_batch stats;
  for (int i = 0; i < 511; ++i)
    assert(!stats.add(37, 2, 1, 721, 4096, false));
  assert(stats.add(9, 1, 0, 1, 1024, true));
  assert(stats.regions == 512 && stats.layers == 1023);
  assert(stats.row_layers == 511 && stats.runs == 511 * 721 + 1);
  assert(stats.requested_bytes == 511 * 4096 + 1024);
  assert(stats.r3d_regions == 1 && stats.dominant_format == 37);
  assert(stats.formats[37] == 511);
  stats = {};
  assert(stats.regions == 0 && stats.formats[37] == 0);
  assert(!stats.add(1000156000, 1, 0, 1, 4, false));
  assert(stats.other_formats == 1);
  const char *eden = "yuzu Emulator";
  assert(amaral_readback_scope(740, 0, eden, eden));
  assert(amaral_readback_scope(0, 0x43050a01ULL, eden, eden));
  assert(amaral_readback_scope(0, 0xffff43050a01ULL, eden, eden));
  assert(amaral_readback_scope(740, 0x43050a01ULL, eden, eden));
  for (auto gpu : {630, 650, 660, 710, 720, 730, 750, 810, 825, 830, 840})
    assert(!amaral_readback_scope(gpu, 0, eden, eden));
  assert(!amaral_readback_scope(0, 0xffff43050c01ULL, eden, eden));
  assert(!amaral_readback_scope(750, 0x43050a01ULL, eden, eden));
  assert(!amaral_readback_scope(740, 0x44030000ULL, eden, eden));
  assert(!amaral_readback_scope(0, 0, eden, eden));
  assert(!amaral_readback_scope(740, 0, nullptr, eden));
  assert(!amaral_readback_scope(740, 0, eden, nullptr));
  assert(!amaral_readback_scope(740, 0, "Cemu", eden));
  assert(!amaral_readback_scope(740, 0, eden, "DXVK"));
  assert(!amaral_readback_scope(740, 0, "yuzu Emulator-other", eden));
}
''')
            binary = pathlib.Path(folder) / "gate"
            subprocess.run(["c++", "-std=c++17", "-Wall", "-Wextra", "-Werror",
                            str(test), "-o", str(binary)], check=True)
            subprocess.run([str(binary)], check=True)
