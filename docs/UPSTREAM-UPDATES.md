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

Uma mudança de commit Mesa justifica incremento minor; correção interna sem
mudança upstream justifica patch. Alteração incompatível de formato ou política
justifica major.

