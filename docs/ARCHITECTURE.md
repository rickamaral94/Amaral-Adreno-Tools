# Arquitetura

- Mesa upstream fixado por SHA completo e build Android ARM64/KGSL genérico.
- `config/patches.json`: fonte única da ordem e variantes; pesquisa não aplicada.
- `tools/apply_patches.py`: exige árvore limpa e SHA exato; falha em drift.
- Standard: NDK, perfis A8xx isolados, fixes de lifetime e remoção de spoof MGS4.
- OneUI: Standard mais TP_UBWC_FLAG_HINT somente nos dois IDs FD740/KGSL.
- `build_universal.sh`: compila, empacota, valida ELF/ZIP e gera catálogo.
- `check_reproducibility.sh`: duas árvores independentes, compara ZIP/ELF/catálogo.
- `build_manifest.py`: SHA fonte, lock, fingerprint, hashes e validação não executada.
- `verify_release_bundle.py`: vincula os assets ao código e à qualificação.
- `promotion_gate.py`: bloqueia promoção sem evidência técnica por família.

Odin 2 Portal é o controle físico A740, não justificativa para defaults globais.
A810/A812/A825 externos continuam isolados. A840 mantém topologias upstream.
Pesquisa de pipeline_binary/VTN/NIR/IR3/WSI segue separada da candidata de estabilidade.
