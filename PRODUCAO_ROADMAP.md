# Roadmap de Producao

Este arquivo sera a base dos proximos ciclos de desenvolvimento ate o Apex estar pronto para producao.

## Como usar este roadmap

- Trabalhar de cima para baixo, uma fase por vez.
- Antes de iniciar uma fase, revisar os criterios de aceite.
- Ao finalizar uma tarefa, marcar o checkbox e registrar observacoes relevantes.
- Evitar novas features fora deste roteiro ate a base de producao estar estavel.

## Fase 1 - Estabilizacao da base

Objetivo: garantir que a aplicacao rode de forma previsivel em ambiente local e em container.

- [x] Documentar comandos locais no `README.md`.
- [x] Criar `.env.example` com todas as variaveis obrigatorias.
- [x] Remover arquivos gerados do repositorio, como `__pycache__`, sessoes locais e bancos locais.
- [x] Criar ou revisar `.gitignore`.
- [ ] Separar configuracoes de desenvolvimento, homologacao e producao.
- [x] Validar `docker-compose.yaml` com app, Redis e worker Celery.
- [ ] Garantir que `wsgi.py` suba sem depender de estado local invisivel.

Observacoes da Fase 1:

- `.dockerignore` criado para evitar cache, sessoes e banco local no build.
- `SECRET_SESSION` e `DATABASE_URL` agora podem vir do ambiente, mantendo defaults de desenvolvimento.
- `docker compose config` validado sem exigir `.env` presente.
- Arquivos gerados foram removidos do versionamento com `git rm --cached`, sem apagar os arquivos locais.

Criterios de aceite:

- Um desenvolvedor novo consegue subir o projeto seguindo apenas o README.
- Nenhum segredo, banco local ou arquivo temporario fica versionado.
- App, worker e Redis iniciam com um unico comando documentado.

## Fase 2 - Configuracao e seguranca

Objetivo: proteger credenciais, sessoes e integracoes externas.

- [ ] Mover `SECRET_KEY`, Redis URL, banco, OpenAI e Serper para variaveis de ambiente.
- [ ] Validar variaveis obrigatorias na inicializacao e exibir erro claro quando faltar algo.
- [ ] Trocar armazenamento de chaves sensiveis do usuario para formato criptografado ou protegido.
- [ ] Mascarar chaves API na interface.
- [ ] Usar campos `password` para credenciais sensiveis em Minha Conta.
- [ ] Adicionar confirmacao antes de sobrescrever credenciais.
- [ ] Revisar expiracao de sessao e cookies seguros para producao.

Criterios de aceite:

- Nenhuma chave sensivel aparece inteira na UI.
- O app falha cedo com mensagem clara se a configuracao estiver incompleta.
- Cookies e sessoes usam configuracao adequada para HTTPS.

## Fase 3 - Banco de dados e migracoes

Objetivo: substituir dependencias frageis de SQLite local por fluxo seguro de banco em producao.

- [ ] Definir banco de producao recomendado.
- [ ] Adicionar Flask-Migrate/Alembic ou fluxo equivalente de migracoes.
- [ ] Criar migracao inicial dos modelos atuais.
- [ ] Remover dependencia de `apex/src/database.db` versionado.
- [ ] Adicionar rotina de backup e restore.
- [ ] Definir indices para buscas frequentes, como usuario e relatorios.

Criterios de aceite:

- Schema do banco e reproduzivel por migracoes.
- Deploy nao depende de copiar arquivo `.db`.
- Existe processo documentado de backup.

## Fase 4 - Celery, tarefas e resiliencia

Objetivo: tornar geracao de relatorios confiavel e observavel.

- [ ] Revisar estados de tarefa: `PENDING`, `SUCCESS`, `FAILURE`, retry e timeout.
- [ ] Definir timeouts para chamadas externas.
- [ ] Implementar retry com backoff para chamadas temporariamente instaveis.
- [ ] Salvar erros de tarefa de forma amigavel para o usuario.
- [ ] Evitar `result.get()` em renderizacao quando puder bloquear a pagina.
- [ ] Criar pagina/estado de processamento com atualizacao previsivel.
- [ ] Definir limpeza de resultados antigos no Redis/Celery.

Criterios de aceite:

- Falhas de API nao quebram a pagina.
- Usuario ve status claro do relatorio.
- Tarefas longas nao travam renderizacao do Dash.

## Fase 5 - Busca e integracoes externas

Objetivo: tornar pesquisa e coleta de resultados mais robustas.

- [ ] Validar SerperAPI antes de permitir pesquisa.
- [ ] Exibir erro amigavel quando Serper retorna erro, limite ou chave invalida.
- [ ] Normalizar resultados sem `title`, `snippet`, `source` ou `link`.
- [ ] Adicionar timeout nas requisicoes HTTP.
- [ ] Registrar metadados da busca para auditoria.
- [ ] Definir limite de resultados por origem.
- [ ] Revisar Twitter/Facebook: manter, remover ou renomear fontes conforme comportamento real.

Criterios de aceite:

- Uma resposta incompleta da API nao quebra a busca.
- Usuario entende quando uma chave esta invalida ou sem limite.
- As abas mostram apenas fontes realmente suportadas.

## Fase 6 - Relatorios e email

Objetivo: melhorar envio, leitura e confiabilidade dos relatorios.

- [ ] Validar email de destino antes do envio.
- [ ] Melhorar feedback de sucesso/erro no modal de envio.
- [ ] Adicionar logs de envio de email.
- [ ] Padronizar template de email com a identidade Apex.
- [ ] Permitir reenviar relatorio sem recarregar toda a pagina.
- [ ] Avaliar anexar PDF ou HTML alem do corpo do email.
- [ ] Proteger iframe/renderizacao de HTML gerado.

Criterios de aceite:

- Envio de email tem mensagem clara para sucesso e falha.
- HTML do relatorio nao cria risco desnecessario para a aplicacao.
- Historico de envio pode ser auditado.

## Fase 7 - UX e interface

Objetivo: deixar a experiencia consistente e pronta para usuarios finais.

- [ ] Revisar responsividade em mobile, tablet e desktop.
- [ ] Padronizar todos os botoes com classes Apex.
- [ ] Padronizar estados vazios, erros e carregamento.
- [ ] Melhorar tela de login com mensagens de erro mais especificas.
- [ ] Revisar textos e corrigir ortografia.
- [ ] Adicionar pagina de instrucoes com links oficiais quando aplicavel.
- [ ] Garantir contraste acessivel nas cores principais.

Criterios de aceite:

- Nao ha botoes azuis padrao fora da identidade definida.
- Todas as paginas tem estado vazio e estado de erro.
- Textos principais estao revisados em portugues.

## Fase 8 - Testes e qualidade

Objetivo: reduzir risco de regressao antes do deploy.

- [ ] Adicionar teste de importacao das paginas Dash.
- [ ] Adicionar testes unitarios para validacao de dados da conta.
- [ ] Adicionar testes para normalizacao de resultados de busca.
- [ ] Adicionar testes para callbacks principais quando viavel.
- [ ] Configurar lint/formatacao.
- [ ] Criar comando unico de verificacao local.
- [ ] Rodar verificacoes em CI.

Criterios de aceite:

- Existe um comando documentado para validar o projeto.
- CI bloqueia mudancas com erro de sintaxe ou teste quebrado.
- Funcoes criticas tem cobertura minima.

## Fase 9 - Observabilidade

Objetivo: saber o que esta acontecendo em producao.

- [ ] Configurar logs estruturados para app e worker.
- [ ] Registrar erros de callbacks e tarefas.
- [ ] Adicionar healthcheck HTTP.
- [ ] Adicionar healthcheck do worker Celery.
- [ ] Monitorar uso de Redis, filas e falhas de tarefas.
- [ ] Definir politica de retencao de logs.
- [ ] Avaliar Sentry ou ferramenta similar para excecoes.

Criterios de aceite:

- E possivel saber se app, worker e Redis estao saudaveis.
- Erros em producao deixam rastros suficientes para debug.
- Falhas de tarefa aparecem em monitoramento.

## Fase 10 - Deploy de producao

Objetivo: publicar com processo repetivel e rollback possivel.

- [ ] Definir servidor, dominio e estrategia de deploy.
- [ ] Configurar Nginx com HTTPS.
- [ ] Revisar `nginx.docker-compose.yaml` e `certbot.docker-compose.yaml`.
- [ ] Configurar Gunicorn para Flask/Dash.
- [ ] Configurar Celery worker separado do web.
- [ ] Criar rotina de deploy step by step.
- [ ] Criar rotina de rollback.
- [ ] Testar renovacao de certificado.

Criterios de aceite:

- Deploy pode ser repetido sem passos manuais ocultos.
- HTTPS funciona.
- Existe plano de rollback.

## Ordem sugerida para as proximas tarefas

1. Criar `.gitignore` e limpar arquivos locais versionados.
2. Criar `.env.example` e validar configuracoes obrigatorias.
3. Documentar setup local no `README.md`.
4. Revisar Docker Compose para app, worker e Redis.
5. Adicionar validacao/mascara dos dados em Minha Conta.
6. Melhorar tratamento de erro da SerperAPI e OpenAI.
7. Criar migracoes de banco.
8. Adicionar testes minimos e CI.
9. Configurar logs e healthchecks.
10. Preparar deploy com Nginx, HTTPS, Gunicorn e Celery.

## Decisoes pendentes

- Banco de producao: Postgres, MySQL ou outro.
- Plataforma de deploy: VPS, cloud provider, PaaS ou container registry.
- Ferramenta de monitoramento de erros.
- Politica de retencao de relatorios gerados.
- Politica de criptografia/armazenamento de chaves dos usuarios.
