# Turnip Amaral 26.3.0-devel v4.2

## A740 Aurora performance release

Target: Qualcomm Adreno 740 / Snapdragon 8 Gen 2.

This release incorporates the community-tested Aurora tuning into the standard Amaral driver build:

- IR3 Global Code Motion enabled for A7XX compiler generation.
- `pipeline_suballoc` increased from 128 KiB to 512 KiB.
- KGSL profiling suballocator increased from 128 KiB to 512 KiB.
- Default Mesa shader cache limit raised from 1 GiB to 4 GiB.
- Turnip Zelda compatibility workarounds enabled: `tu_dont_care_as_load` and `tu_allow_oob_indirect_ubo_loads`.
- Existing Amaral FD740 depth-extension and A825 experimental patches retained.

## Package names

Standard: `turnip_amaral_26.3.0-devel_v4.2.zip`

OneUI: `turnip_amaral_26.3.0-devel_v4.2_oneUI.zip`

This is a performance-oriented experimental release. Validate on real Adreno 740 hardware with Amaral Driver Lab before treating the tuning as universal.
