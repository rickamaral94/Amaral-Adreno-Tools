# Atualizações do Mesa

O `main` do Mesa é monitorado, mas nunca consumido automaticamente em uma
release. O processo de atualização é:

1. detectar a nova cabeça upstream;
2. abrir uma branch e atualizar somente `config/mesa-lock.json`;
3. auditar todos os commits entre o lock antigo e o novo, com atenção a
   `src/freedreno`, Vulkan runtime, Android, WSI, compiler, NIR e build system;
4. reaplicar cada patch com `git apply --check` e revisar o diff resultante;
5. gerar duas builds independentes e exigir SHA-256 idêntico;
6. validar ELF, ABI, dependências, hardening e `meta.json`;
7. executar Driver Lab contra a release anterior em A6xx/A7xx/A8xx;
8. publicar primeiro alpha/RC; promover apenas após retorno suficiente.

A release prévia nunca substitui automaticamente a estável/latest. A promoção
é uma decisão explícita depois da validação comunitária; enquanto isso, a
release estável anterior permanece destacada como fallback.

## Versionamento curto

O nome público usa `Turnip Amaral <Mesa> v<revisão>`. A revisão Amaral começa em
`v1`, avança enquanto a versão Mesa permanecer igual e volta para `v1` quando a
versão Mesa mudar. O commit upstream completo permanece no lock e no registro
da release para garantir rastreabilidade sem alongar o nome do driver.
