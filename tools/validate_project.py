#!/usr/bin/env python3
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]


def load(relative):
    with (ROOT / relative).open(encoding="utf-8") as stream:
        return json.load(stream)


def read_text(relative):
    return (ROOT / relative).read_text(encoding="utf-8")


def main():
    lock = load("config/mesa-lock.json")
    evidence = load("evidence/candidates.json")
    sources = load("evidence/sources.json")

    commit = lock["mesa"]["commit"]
    assert re.fullmatch(r"[0-9a-f]{40}", commit), "Mesa commit must be a full SHA"
    assert isinstance(lock["amaral_revision"], str)
    assert lock["amaral_revision"] == "4.5"
    assert lock["build"]["cpu"] == "armv8-a"
    assert lock["build"]["kmd"] == "kgsl"
    assert sources["primary"][0]["name"] == "Mesa 3D"

    ids = set()
    for item in evidence["candidates"]:
        assert item["id"] not in ids, f"duplicate candidate: {item['id']}"
        ids.add(item["id"])
        assert item["status"] in {
            "proposed", "testing", "approved", "active",
            "reference-only", "rejected"
        }
        if item["kind"].startswith("runtime") and item["status"] == "active":
            gate = item.get("gate", {})
            assert gate.get("visual_pass") is True
            assert gate.get("minimum_runs", 0) >= 5
            assert gate.get("confidence") in {"medium", "high"}
            assert gate.get("families") == ["A6xx", "A7xx", "A8xx"]
        if item.get("patch"):
            assert (ROOT / item["patch"]).is_file(), item["patch"]

    a825_patch = read_text("patches/0002-a825-experimental.patch")
    assert 'GPUId(chip_id=0x44030000, name="Adreno (TM) 825")' in a825_patch
    assert "gmem_ccu_color_cache_fraction = CCUColorCacheFraction.HALF.value" in a825_patch
    assert "gmem_per_ccu_color_cache_size = 128 * 1024" in a825_patch
    assert "gmem_ccu_depth_cache_fraction = CCUColorCacheFraction.HALF.value" in a825_patch
    assert "gmem_per_ccu_depth_cache_size = 128 * 1024" in a825_patch
    assert "tile_align_w = 64" in a825_patch
    assert "shading_rate_matches_vk = True" not in a825_patch
    assert "tu_pipeline.cc" not in a825_patch
    assert "is_target_gpu" not in a825_patch
    assert "cs_shared_mem_size = 64 * 1024" in a825_patch
    assert "const bool is_a810" not in a825_patch
    assert "const bool is_a829" not in a825_patch
    assert "const bool is_a830" not in a825_patch
    assert "const bool is_a840" not in a825_patch

    oneui_patch = read_text("patches/0003-oneui-ubwc.patch")
    assert oneui_patch.count("enable_tp_ubwc_flag_hint = True") == 1
    assert "0x44030000" not in oneui_patch
    assert oneui_patch.count('GPUId(chip_id=0x43050a01, name="FD740")') == 2
    assert oneui_patch.count('GPUId(chip_id=0xffff43050a01, name="FD740")') == 2
    assert "GPUId(740)" in oneui_patch
    assert "0xffff43050c01" in oneui_patch
    assert "restrito às entradas KGSL da FD740" in oneui_patch

    # v4.4: o gate por chip_id saiu. Ele marcava onde estava a evidencia, nao
    # uma dependencia tecnica. Cada extensao passou a ser gateada pela sua
    # dependencia real, e sao diferentes - por isso as duas sao afirmadas
    # separadamente aqui.
    depth_patch = read_text("patches/0004-depth-extensions.patch")

    # depth_bias_control: sem gate. O runtime do Vulkan faz o trabalho e
    # tu6_emit_depth_bias() nao tem ramificacao por chip.
    assert "EXT_depth_bias_control = true" in depth_patch
    assert "features->depthBiasControl = true" in depth_patch
    assert "features->depthBiasExact = true" in depth_patch
    # Suporte parcial continua declarado como parcial. Ligar qualquer uma
    # destas seria afirmar controle que o Adreno nao tem.
    assert "features->leastRepresentableValueForceUnormRepresentation = false" in depth_patch
    assert "features->floatRepresentation = false" in depth_patch

    # depth_range_unrestricted: a7xx+, e este gate e' de silicio. No a6xx o
    # hardware clampa sozinho e a extensao nao teria como ser honrada, entao
    # declara-la sem condicao seria mentir. Esta guarda existe para impedir
    # exatamente isso.
    assert "EXT_depth_range_unrestricted = device->info->chip >= 7" in depth_patch
    assert "EXT_depth_range_unrestricted = true" not in depth_patch

    # O predicado por chip_id nao deve voltar por descuido.
    assert "tu_is_fd740_kgsl" not in depth_patch
    assert "0x43050a01" not in depth_patch

    assert "force_sysmem" not in depth_patch
    assert "0008-android-shader-cache" not in depth_patch

    aurora_patch = read_text("patches/0005-a740-aurora-performance.patch")
    assert "compiler->reg_size_vec4 >= 96" in aurora_patch
    assert aurora_patch.count("512 * 1024") == 2
    assert "compiler->gen >= 7" not in aurora_patch

    zelda_patch = read_text("patches/0006-emulator-compat-driconf.patch")
    assert 'application_name_match=".*(botw).*"' in zelda_patch
    assert 'application_name_match=".*(totk).*"' in zelda_patch
    assert zelda_patch.count('tu_autotune_algorithm" value="prefer_gmem') == 2
    # Uma linha e' contexto upstream (Sons of the Forest), a outra e' TOTK.
    assert zelda_patch.count('tu_ignore_frag_depth_direction" value="true') == 2
    assert '<option name="tu_emulate_alpha_to_coverage"' not in zelda_patch
    assert "engine_name_match=\"yuzu Emulator\"" not in zelda_patch
    assert "TU_DEBUG=gmem" in zelda_patch  # só comentário explícito de não uso

    candidate_ids = {item["id"] for item in evidence["candidates"]}
    assert "aurora-gcm-and-suballocators" in candidate_ids
    assert "zelda-botw-totk-title-profile" in candidate_ids
    assert "broad-emulator-driconf" in candidate_ids

    print("Project metadata and evidence gates are valid.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (AssertionError, KeyError, json.JSONDecodeError) as exc:
        print(f"validation failed: {exc}", file=sys.stderr)
        sys.exit(1)
