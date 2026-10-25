# Atualização e promoção

`publish-upstream.yml` permanece agendado em `7 10 1,16 * *` e manual.
Ele busca Mesa oficial, compara com o lock e persiste `evidence/upstream-review.json`.
Não muda o driver, não compila e não publica Latest: caminhos alterados são triagem,
não justificativa de release. A revisão quinzenal externa continua independente.

Após revisão do diff, selecionar SHA completo e justificar problema, mecanismo,
GPUs, regressões e testes. Atualizar lock e preparar candidata com
`python3 tools/release_version.py candidate --mesa-src <árvore-no-SHA> --write`.
Isso preserva stable_version e last_released_mesa_commit; mudanças somente de
Mesa também podem gerar candidata. Registrar notas técnicas antes do merge.

PRs e pushes passam checks rápidos e aplicação em Mesa oficial. Publicação exige
execução manual de `publish-candidate.yml` depois da revisão técnica. Para apenas
compilar, executar `build-candidate.yml`, que não publica. O publicador manual
chama um único workflow reutilizável: Standard e OneUI em
paralelo, duas builds independentes por variante. Downloads NDK são verificados
mesmo quando vêm do cache. Não há cache de compilação no gate de reprodutibilidade.

A publicação verifica o SHA do repositório, manifestos, ZIP/ELF/meta/dependências,
reprodutibilidade e hashes. Publica somente pre-release e confere que Latest ficou
inalterada. Falhas preservam logs; retry usa o mesmo SHA e nunca substitui asset
diferente. Rascunhos ambíguos exigem investigação, não exclusão automática.

Promoção é manual e só passa com o registro descrito em EVIDENCE-POLICY.md.
Os mesmos binários são promovidos; não recompilar para promoção.
O workflow antigo de promoção especial A840 foi retirado.

Ubuntu e pacotes host são registrados, mas ainda não formam imagem hermética
fixada por digest. A igualdade observada é de duas builds na execução registrada;
não se afirma reprodução futura entre qualquer ambiente.
