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
- [x] Separar configuracoes de desenvolvimento, homologacao e producao.
- [x] Validar `docker-compose.yaml` com app, Redis e worker Celery.
- [x] Garantir que `wsgi.py` suba sem depender de estado local invisivel.

Observacoes da Fase 1:

- `.dockerignore` criado para evitar cache, sessoes e banco local no build.
- `SECRET_SESSION` e `DATABASE_URL` agora podem vir do ambiente, mantendo defaults de desenvolvimento.
- `docker compose config` validado sem exigir `.env` presente.
- Arquivos gerados foram removidos do versionamento com `git rm --cached`, sem apagar os arquivos locais.
- SQLite em Docker movido para volume persistente `apex-data` em `/app/data/apex.db`.
- `create-db` executado no container e tabelas `user`/`searchresults` confirmadas.
- Configuracoes separadas por `ENVIRONMENT=development|staging|production`, com exemplos `.env.*.example`.
- Staging/producao usam cookies seguros quando `SESSION_COOKIE_SECURE=true`.

Criterios de aceite:

- Um desenvolvedor novo consegue subir o projeto seguindo apenas o README.
- Nenhum segredo, banco local ou arquivo temporario fica versionado.
- App, worker e Redis iniciam com um unico comando documentado.

## Fase 2 - Configuracao e seguranca

Objetivo: proteger credenciais, sessoes e integracoes externas.

- [x] Mover `SECRET_KEY`, Redis URL e banco para variaveis de ambiente.
- [x] Validar variaveis obrigatorias na inicializacao e exibir erro claro quando faltar algo.
- [x] Trocar armazenamento de chaves sensiveis do usuario para formato criptografado ou protegido.
- [x] Mascarar chaves API na interface.
- [x] Usar campos `password` para credenciais sensiveis em Minha Conta.
- [x] Adicionar confirmacao antes de sobrescrever credenciais.
- [x] Revisar expiracao de sessao e cookies seguros para producao.

Observacoes da Fase 2:

- OpenAI e Serper continuam como credenciais por usuario em Minha Conta; a protecao definitiva depende do item de criptografia em banco.
- `staging` e `production` falham na inicializacao quando `SECRET_SESSION`, `REDIS_HOST`, `DATABASE_URL` ou cookies seguros estao ausentes/inseguros.
- Campos `Senha SMTP`, `Chave API OpenAI` e `Chave SerperAPI` agora usam input de senha.
- A aba de relatorio exibe chave OpenAI mascarada.
- Salvar credenciais exige confirmacao explicita.
- Bootstrap `admin/admin` removido; admin inicial agora exige comando/variaveis explicitas.
- Administracao em `/admin` passou a ser uma pagina Dash propria para usuarios `admin=True`, com criacao de tenants e usuarios; Flask-Admin foi removido da carga da aplicacao.
- Credenciais sensiveis de usuario (`api_key`, `serpapi_key`, `stmp_password`) sao criptografadas em banco com `CREDENTIALS_SECRET_KEY`; campos sensiveis nao sao mais pre-preenchidos na pagina Minha Conta.

Criterios de aceite:

- Nenhuma chave sensivel aparece inteira na UI.
- O app falha cedo com mensagem clara se a configuracao estiver incompleta.
- Cookies e sessoes usam configuracao adequada para HTTPS.

## Fase 3 - Banco de dados e migracoes

Objetivo: substituir dependencias frageis de SQLite local por fluxo seguro de banco em producao.

Pre-requisito multi-tenant:

- [x] Criar modelo `Tenant` e associar usuarios/relatorios ao tenant.
- [x] Resolver tenant por subdominio usando `ROOT_DOMAIN`.
- [x] Adicionar comandos para criar tenant e usuario por tenant.
- [x] Transformar compatibilidade multi-tenant atual em migracoes formais.

- [x] Definir banco de producao recomendado.
- [x] Adicionar Flask-Migrate/Alembic ou fluxo equivalente de migracoes.
- [x] Criar migracao inicial dos modelos atuais.
- [x] Remover dependencia de `apex/src/database.db` versionado.
- [x] Adicionar rotina de backup e restore.
- [x] Definir indices para buscas frequentes, como usuario e relatorios.

Observacoes da Fase 3:

- PostgreSQL externo definido como banco recomendado para staging/producao; Docker Compose sobe PostgreSQL local para desenvolvimento com `COMPOSE_PROFILES=local-db`.
- Flask-Migrate/Alembic configurado em `apex/migrations`, com migracao inicial e indices adicionais para consultas por tenant, usuario, data e `result_id`.
- `flask db upgrade` passa a ser o fluxo principal de schema; `create-db` fica como apoio para criar/preencher tenant padrao em bancos antigos.
- Backup/restore disponivel via `flask backup-database` e `flask restore-database`, usando API nativa do SQLite ou `pg_dump`/`pg_restore` em PostgreSQL.
- `apex/src/database.db` esta ignorado pelo git e o deploy nao depende de banco local versionado.

Criterios de aceite:

- Schema do banco e reproduzivel por migracoes.
- Deploy nao depende de copiar arquivo `.db`.
- Existe processo documentado de backup.

## Fase 4 - Celery, tarefas e resiliencia

Objetivo: tornar geracao de relatorios confiavel e observavel.

- [x] Revisar estados de tarefa: `PENDING`, `SUCCESS`, `FAILURE`, retry e timeout.
- [x] Definir timeouts para chamadas externas.
- [x] Implementar retry com backoff para chamadas temporariamente instaveis.
- [x] Salvar erros de tarefa de forma amigavel para o usuario.
- [x] Evitar `result.get()` em renderizacao quando puder bloquear a pagina.
- [x] Criar pagina/estado de processamento com atualizacao previsivel.
- [x] Definir limpeza de resultados antigos no Redis/Celery.

Observacoes da Fase 4:

- `report_media_task` agora usa `track_started`, time limits de tarefa, retry automatico com backoff e limite de tentativas.
- A tela de relatorios diferencia `PENDING`, `STARTED`, `RETRY`, `SUCCESS` e `FAILURE`.
- `result.get()` ficou restrito ao estado `SUCCESS` ou a acoes explicitas de envio, evitando bloqueio durante processamento.
- Timeouts configuraveis foram adicionados para scraping de artigos, OpenAI e SMTP.
- Erros tecnicos de geracao de relatorio sao convertidos em mensagens amigaveis para a UI.
- Resultados Celery no Redis expiram via `CELERY_RESULT_EXPIRES_SECONDS`, com default de 7 dias.

Criterios de aceite:

- Falhas de API nao quebram a pagina.
- Usuario ve status claro do relatorio.
- Tarefas longas nao travam renderizacao do Dash.

## Fase 5 - Busca e integracoes externas

Objetivo: tornar pesquisa e coleta de resultados mais robustas.

- [x] Validar SerperAPI antes de permitir pesquisa.
- [x] Exibir erro amigavel quando Serper retorna erro, limite ou chave invalida.
- [x] Normalizar resultados sem `title`, `snippet`, `source` ou `link`.
- [x] Adicionar timeout nas requisicoes HTTP.
- [x] Registrar metadados da busca para auditoria.
- [x] Definir limite de resultados por origem.
- [x] Revisar Twitter/Facebook: manter, remover ou renomear fontes conforme comportamento real.

Observacoes da Fase 5:

- Busca valida a chave SerperAPI antes de consultar as fontes.
- Erros de chave invalida, limite, timeout e resposta invalida sao exibidos como mensagens amigaveis.
- Resultados incompletos sao normalizados antes de renderizar cards e opcoes de relatorio.
- `SEARCH_RESULTS_PER_SOURCE` controla o limite por origem.
- Metadados de auditoria sao salvos em `search_audit` com tenant, usuario, query, status, contagens e erro.
- A aba Google foi renomeada para Google News e a aba Twitter para X/Twitter, refletindo as fontes realmente consultadas.

Criterios de aceite:

- Uma resposta incompleta da API nao quebra a busca.
- Usuario entende quando uma chave esta invalida ou sem limite.
- As abas mostram apenas fontes realmente suportadas.

## Fase 6 - Relatorios e email

Objetivo: melhorar envio, leitura e confiabilidade dos relatorios.

- [x] Validar email de destino antes do envio.
- [x] Melhorar feedback de sucesso/erro no modal de envio.
- [x] Adicionar logs de envio de email.
- [x] Padronizar template de email com a identidade Apex.
- [x] Permitir reenviar relatorio sem recarregar toda a pagina.
- [x] Avaliar anexar PDF ou HTML alem do corpo do email.
- [x] Proteger iframe/renderizacao de HTML gerado.

Observacoes da Fase 6:

- Criada auditoria de envio em `email_audit`, com tenant, usuario, relatorio, task Celery, destinatario, status e erro.
- O envio agora valida email com parser padrao e padrao minimo `usuario@dominio`.
- Falhas de SMTP e credenciais ausentes retornam mensagem amigavel no modal.
- O template de email foi centralizado com cabecalho e rodape Apex.
- O HTML do relatorio e sanitizado antes de ir para o iframe e para o email.
- O iframe usa `sandbox` sem permissoes extras para reduzir risco de execucao de conteudo ativo.
- Nao foi adicionado anexo nesta etapa: o HTML segue no corpo do email para manter compatibilidade simples e evitar arquivos gerados sem politica de retencao.

Criterios de aceite:

- Envio de email tem mensagem clara para sucesso e falha.
- HTML do relatorio nao cria risco desnecessario para a aplicacao.
- Historico de envio pode ser auditado.

## Fase 7 - UX e interface

Objetivo: deixar a experiencia consistente e pronta para usuarios finais.

- [x] Revisar responsividade em mobile, tablet e desktop.
- [x] Padronizar todos os botoes com classes Apex.
- [x] Padronizar estados vazios, erros e carregamento.
- [x] Melhorar tela de login com mensagens de erro mais especificas.
- [x] Revisar textos e corrigir ortografia.
- [x] Adicionar pagina de instrucoes com links oficiais quando aplicavel.
- [x] Garantir contraste acessivel nas cores principais.

Observacoes da Fase 7:

- A tela de login agora diferencia campos obrigatorios, credenciais invalidas e tenant nao encontrado.
- Botoes primarios, secundarios e perigosos usam classes Apex, evitando botoes azuis padrao.
- Acoes perigosas usam vermelho com contraste mais forte e estados hover dedicados.
- A navegacao e os formularios receberam ajustes responsivos para telas menores.
- A pagina de instrucoes da conta ganhou links oficiais para Google, senha de aplicativo, OpenAI e Serper.
- Textos principais de login, busca, admin, perfil, relatorios e envio de email foram revisados em portugues.
- Estados vazios e de erro foram alinhados com a identidade visual Apex.

Criterios de aceite:

- Nao ha botoes azuis padrao fora da identidade definida.
- Todas as paginas tem estado vazio e estado de erro.
- Textos principais estao revisados em portugues.

## Fase 8 - Fluxo de valor, relatorio e funcionalidade

Objetivo: transformar o Apex em um fluxo mais claro de monitoramento, analise, aprovacao e envio de relatorios ao cliente.

- [ ] Redesenhar o fluxo principal: pesquisar, selecionar fontes, gerar analise, revisar, aprovar e enviar.
- [x] Criar uma nova UI para emissao de relatorio, com etapas visiveis e estado claro de progresso.
- [x] Melhorar o prompt e a estrutura da analise gerada pela IA.
- [x] Padronizar o relatorio gerado com secoes de resumo executivo, principais achados, riscos, oportunidades, recomendacoes e fontes.
- [x] Criar uma visualizacao propria do relatorio gerado, sem depender apenas de iframe bruto.
- [x] Permitir revisar o relatorio antes do envio ao cliente.
- [x] Permitir editar assunto, mensagem de acompanhamento e destinatario antes do envio.
- [x] Melhorar a qualidade visual do email enviado ao cliente.
- [x] Registrar status do relatorio: rascunho, gerando, pronto, revisado, enviado e falha.
- [x] Adicionar historico de envios por relatorio.
- [x] Definir campos minimos do relatorio para auditoria e recuperacao futura.
- [x] Avaliar salvar snapshot HTML sanitizado do relatorio no banco ou em storage.
- [x] Levantar funcionalidades novas para aumentar valor do produto.

Novo fluxo proposto:

1. Usuario pesquisa um tema.
2. Sistema exibe resultados por origem com filtros, contagem e selecao.
3. Usuario seleciona os conteudos relevantes.
4. Usuario abre uma tela de "Novo Relatorio" com resumo da selecao.
5. Usuario escolhe tipo de relatorio, tom, publico-alvo e objetivo.
6. Celery gera a analise com IA em segundo plano.
7. Usuario revisa o relatorio em uma pagina propria.
8. Usuario aprova, ajusta mensagem de email e envia ao cliente.
9. Sistema registra envio, destinatario, data, status e erro quando houver.

Estrutura sugerida para o relatorio:

- Resumo executivo.
- Contexto da busca.
- Principais achados.
- Sentimento geral e leitura estrategica.
- Riscos de imagem ou reputacao.
- Oportunidades de comunicacao.
- Recomendacoes praticas.
- Conteudos analisados com fonte e link.
- Observacoes metodologicas.

Melhorias sugeridas para a IA:

- Prompt com persona clara de analista de comunicacao estrategica.
- Instrucao para citar somente fatos presentes nas fontes selecionadas.
- Separacao entre fatos, inferencias e recomendacoes.
- Pontuacao de relevancia por item analisado.
- Sinalizacao de baixa confianca quando houver poucos dados.
- Saida em JSON estruturado antes de renderizar HTML.
- Template HTML gerado a partir de dados estruturados, nao texto livre inteiro.

Possiveis funcionalidades futuras:

- Biblioteca de modelos de relatorio por objetivo: clipping, crise, reputacao, concorrencia e pauta.
- Tags ou categorias nos resultados selecionados.
- Campo de cliente/campanha associado ao relatorio.
- Filtro por periodo, origem, palavra-chave e sentimento.
- Score de relevancia das noticias.
- Comparacao entre pesquisas ou periodos.
- Comentarios internos antes de enviar ao cliente.
- Aprovacao por outro usuario admin antes do envio.
- Exportacao em PDF.
- Link publico protegido para o cliente acessar o relatorio.
- Agendamento de pesquisas recorrentes.
- Alertas por email quando uma busca recorrente encontrar novos resultados.
- Dashboard por tenant com volume de pesquisas, relatorios e envios.
- Lista de contatos/clientes por tenant para envio rapido.
- Identidade visual por tenant no relatorio e email.

Observacoes da Fase 8:

- A emissao de relatorio ganhou configuracoes de tipo, tom, publico-alvo e objetivo antes de disparar a tarefa.
- A tarefa Celery agora recebe essas configuracoes e orienta a IA com persona de analista de comunicacao estrategica.
- A IA passa a gerar uma estrutura JSON para resumo executivo, contexto, achados, sentimento, riscos, oportunidades, recomendacoes e metodologia.
- O HTML final do relatorio e renderizado por template controlado pela aplicacao a partir dos dados estruturados.
- A tela de relatorios mostra uma revisao estruturada do relatorio antes do envio ao cliente.
- O envio ao cliente ganhou campos editaveis de destinatario, assunto e mensagem de acompanhamento.
- `searchresults` recebeu campos de status, configuracoes do relatorio, snapshot HTML/JSON e datas de revisao/envio.
- O historico de envio segue registrado em `email_audit`, agora associado ao novo fluxo de revisao/envio.

Criterios de aceite:

- O usuario entende o caminho completo do trabalho sem precisar de explicacao externa.
- Relatorio gerado tem estrutura consistente e util para decisao.
- Email ao cliente parece uma entrega profissional, nao apenas HTML gerado.
- Relatorio pode ser revisado antes do envio.
- Status e historico do relatorio ficam claros.

## Fase 9 - Testes e qualidade

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

## Fase 10 - Observabilidade

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

## Fase 11 - Deploy de producao

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
8. Redesenhar o fluxo de valor do relatorio e envio ao cliente.
9. Melhorar prompt, estrutura e visualizacao do relatorio gerado.
10. Adicionar testes minimos e CI.
11. Configurar logs e healthchecks.
12. Preparar deploy com Nginx, HTTPS, Gunicorn e Celery.

## Decisoes pendentes

- Banco de producao: Postgres, MySQL ou outro.
- Plataforma de deploy: VPS, cloud provider, PaaS ou container registry.
- Ferramenta de monitoramento de erros.
- Politica de retencao de relatorios gerados.
- Politica de criptografia/armazenamento de chaves dos usuarios.
- Formato definitivo do relatorio: HTML estruturado, JSON renderizado, PDF ou combinacao.
- Nivel de edicao manual permitido antes do envio ao cliente.
- Necessidade de aprovacao interna antes de enviar relatorios.
