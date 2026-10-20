# Política de evidência

A ordem é correção, compatibilidade, estabilidade e desempenho medido.
Todas as mudanças, inclusive upstream e fixes comunitários, entram como candidata.
A antiga exceção de promoção direta comunitária não se aplica a novas releases.
Autorizações históricas não constituem evidência de CTS ou hardware.

O arquivo `config/patches.json` distingue distribuição e pesquisa.
Não expor capabilities incompletas, copiar registradores por analogia, forçar
GMEM/SYSMEM globalmente, generalizar UBWC ou importar blobs proprietários.

Generalização: L0 dispositivo; L1 família; L2 mecanismo demonstrado entre famílias;
L3 somente universal. Capacidade de hardware semelhante não prova ganho de tuning.

Promoção exige `evidence/qualifications/<versão>.json`, com:
- version, mesa_commit e patchset_sha256 correspondentes à candidata;
- artifacts.standard/oneui.zip_sha256 e elf_sha256;
- ci, reproducibility, cts, vvl, hardware e regressions com status pass e evidence;
- hardware.families cobrindo A6xx/A7xx/A8xx para promoção universal;
- ab com status pass, rounds >= 5, thermal_gate e evidence;
- reviewer e reviewed_at.

O workflow confere os hashes reais dos assets antes de promover. A validação
estrutural do registro não substitui revisão humana dos logs e resultados.
Nunca preencher pass sem executar o teste. Falta de hardware fica not-run.

Para A/B: mesma cena, frontend/jogo/configuração, resolução, clocks e estado de
cache; ordem AB/BA balanceada e cinco rodadas. Definir limite térmico antes do
ensaio e invalidar rodada que ultrapasse o limite. Registrar pixels, crashes,
device lost, FPS, 1% low, P95/P99, stutter, CPU/GPU quando disponível, memória,
temperatura e consumo quando disponível. Medida ausente não é zero.
