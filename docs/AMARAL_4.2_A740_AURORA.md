# Amaral Turnip 4.2 — A740 Aurora Profile

Mesa 26.3.0-devel based experimental profile for Qualcomm Adreno 740 / Snapdragon 8 Gen 2.

## Imported Aurora-derived experiments

- IR3 Global Code Motion (`gcm=1`) for shader scheduling/optimization.
- 4 GiB on-disk shader cache target to reduce shader cache churn in large games.
- 512 KiB pipeline and KGSL profiling suballocator pools, derived from Aurora's 128 KiB → 512 KiB tuning.
- Zelda TOTK/BOTW compatibility path using `tu_dont_care_as_load=true` and `tu_allow_oob_indirect_ubo_loads=true`.

## Scope

This profile is **A740-specific and experimental**. These changes are not enabled globally for every Adreno GPU. The goal is to validate Aurora's performance-oriented changes on Snapdragon 8 Gen 2 hardware through Amaral Driver Lab telemetry and emulator workloads.

## Validation targets

Compare 4.2 A740 Aurora against Amaral 4.1 baseline using:

- FPS average / 1% low
- frametime P50/P95/P99
- shader compilation stutter
- GPU utilization and clocks
- temperature
- crashes / rendering regressions
- TOTK/BOTW artifact behavior

## Important

The profile is an experimental integration of Aurora-described tuning. It should not be treated as proof that every modification improves every workload. Changes that regress stability, image quality, thermals or frametime consistency should be reverted after testing.
