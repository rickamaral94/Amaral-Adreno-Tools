#!/usr/bin/env python3
"""Android HAL dependency/export checks; Mesa links hardware/log/nativewindow/sync stubs."""
import re
import subprocess
import sys

ALLOWED = {'libc.so', 'libm.so', 'libdl.so', 'liblog.so', 'libz.so', 'libandroid.so', 'libnativewindow.so', 'libsync.so', 'libhardware.so'}
# Mesa src/vulkan/vulkan-icd-android-symbols.txt exports the Android HAL HMI.
# Desktop ICD negotiation exports are not required by this Android build.
REQUIRED_EXPORTS = {'HMI'}


def validate(dynamic, symbols):
    needed = set(re.findall(r'\(NEEDED\).*?\[(.*?)\]', dynamic))
    if not needed or needed - ALLOWED:
        raise ValueError(f'Unexpected Android dependencies: {sorted(needed - ALLOWED)}; all={sorted(needed)}')
    exported = {line.split()[-1].split('@')[0] for line in symbols.splitlines()
                if len(line.split()) >= 8 and line.split()[6] != 'UND'}
    if REQUIRED_EXPORTS - exported:
        raise ValueError(f'Missing ICD exports: {sorted(REQUIRED_EXPORTS - exported)}')
    if '(RPATH)' in dynamic or '(RUNPATH)' in dynamic:
        raise ValueError('Host RPATH/RUNPATH is not allowed')
    return sorted(needed)


if __name__ == '__main__':
    dynamic = subprocess.check_output(['readelf', '-dW', sys.argv[1]], text=True)
    symbols = subprocess.check_output(['readelf', '--dyn-syms', '-W', sys.argv[1]], text=True)
    print('Android DT_NEEDED:', ', '.join(validate(dynamic, symbols)))
