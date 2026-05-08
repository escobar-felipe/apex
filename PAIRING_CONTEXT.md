# Contexto do Projeto Apex

Este documento resume o estado geral do projeto para apoiar as sessoes de pareamento e orientar as proximas decisoes de desenvolvimento.

## Visao geral

O Apex e uma aplicacao Flask/Dash para pesquisa de conteudos, organizacao de resultados, geracao de relatorios com IA e envio por email. O usuario informa um termo de busca, revisa resultados por origem, seleciona textos relevantes e dispara uma tarefa assíncrona para gerar analise/relatorio.

O projeto esta em fase de preparacao para producao. As fases 1 a 7 do roadmap ja cobrem estabilizacao, configuracao, seguranca, banco, multi-tenant, Celery, busca externa, envio de email e padronizacao inicial de UX. Antes de iniciar testes e CI, o foco atual e a nova Fase 8: melhorar o fluxo de valor do produto, a qualidade do relatorio gerado, a revisao do relatorio e o envio profissional ao cliente.

## Stack principal

- Backend web: Flask.
- Interface: Dash, Dash Bootstrap Components e Dash Mantine Components.
- Autenticacao: Flask-Login.
- Banco: SQLAlchemy com Flask-Migrate/Alembic.
- Banco recomendado para producao: PostgreSQL externo.
- Banco local em Docker: PostgreSQL via profile `local-db`.
- Sessao, cache, broker e resultado de tarefas: Redis.
- Tarefas assíncronas: Celery.
- Relatorios com IA: OpenAI API, chamada a partir de utilitarios em `apex/src/utils`.
- Busca externa: SerperAPI/Google Search via utilitarios de busca.
- Deploy: Docker Compose com servicos separados para app, worker Celery, Redis e PostgreSQL local de desenvolvimento.

## Estrutura relevante

- `README.md`: comandos de setup, migracoes, criacao de usuarios, ambientes e verificacoes basicas.
- `PRODUCAO_ROADMAP.md`: roteiro principal ate producao.
- `docker-compose.yaml`: stack local com `apex`, `celery`, `redis` e `postgres` opcional.
- `nginx.docker-compose.yaml`: composicao separada para Nginx em servidor.
- `certbot.docker-compose.yaml`: composicao separada para Certbot.
- `apex/src/app.py`: fabrica da aplicacao Flask, configuracao de sessao, cache, banco e Celery.
- `apex/src/dash.py`: instancia principal do Dash.
- `apex/src/models.py`: modelos `Tenant`, `User`, `SearchResult`, auditoria de busca e auditoria de email.
- `apex/src/ext/`: extensoes Flask, comandos CLI, banco, migracoes, auth, Celery, cache, sessao e admin.
- `apex/src/pages/`: paginas Dash.
- `apex/src/pages/admin/page.py`: area administrativa propria para criar tenants e usuarios.
- `apex/src/callbacks/`: callbacks de login, busca, perfil, navbar, resultados e relatorios.
- `apex/src/pages/home/tasks.py`: tarefa Celery de geracao de relatorio.
- `apex/migrations/`: migracoes Alembic.

## Fluxo funcional

1. Usuario autentica no Apex.
2. A pagina inicial valida se a conta tem email, senha SMTP, chave OpenAI e chave SerperAPI.
3. Usuario pesquisa um termo.
4. O callback de busca chama utilitarios de pesquisa, monta cards e prepara os textos selecionaveis para relatorio.
5. Usuario escolhe textos e clica em gerar relatorio.
6. O callback de relatorio dispara `report_media_task` no Celery e salva um `SearchResult` com o `result_id` da tarefa.
7. A tela de meus relatorios consulta os resultados e deve acompanhar o processamento/resultado da tarefa.

## Dados e multi-tenant

O app ja possui base multi-tenant:

- `Tenant`: organiza clientes/empresas por `slug`, dominio opcional e status.
- `User`: pertence a um tenant e possui credenciais de API/email.
- `SearchResult`: guarda pesquisas/relatorios associados a usuario, tenant e tarefa Celery.

O tenant e resolvido por subdominio quando `ROOT_DOMAIN` esta configurado. Em localhost, dominio raiz ou IP local, o app usa `DEFAULT_TENANT_SLUG`.

Usuarios com `admin=True` acessam `/admin` para criar tenants e usuarios por tenant. Essa tela substitui o uso de Flask-Admin.

Credenciais sensiveis de usuario sao criptografadas em banco usando `CREDENTIALS_SECRET_KEY`. Essa chave precisa ser preservada por ambiente; se ela mudar, credenciais ja criptografadas nao poderao ser descriptografadas.

## Ambiente e comandos uteis

Setup Docker de desenvolvimento:

```bash
cp .env.development.example .env
docker compose up --build
docker compose exec apex flask db upgrade
docker compose exec apex flask create-db
docker compose exec apex flask add-user --tenant default --username admin --password senha_forte --admin
```

Acesso local:

```text
http://localhost:5000
```

Verificacoes basicas documentadas:

```bash
python -m compileall apex/src/pages apex/src/callbacks apex/src/utils
git diff --check
```

## Pontos de atencao atuais

- O fluxo funcional ainda parece mais tecnico do que orientado a entrega: pesquisar, selecionar, gerar, revisar e enviar precisam parecer uma jornada unica.
- O relatorio gerado precisa de estrutura consistente e util para decisao, nao apenas texto livre da IA.
- A visualizacao do relatorio ainda depende muito de HTML em iframe.
- O envio ao cliente precisa parecer uma entrega profissional, com assunto, mensagem e revisao antes do disparo.
- Testes e CI ainda nao parecem estar estabelecidos.
- Observabilidade e healthchecks ainda estao pendentes.

## Direcao recomendada para o proximo ciclo

Executar a Fase 8 antes dos testes:

1. Definir o novo fluxo de "Novo Relatorio".
2. Alterar a geracao para produzir dados estruturados, preferencialmente JSON validavel.
3. Renderizar o relatorio a partir de um template controlado pela aplicacao.
4. Criar uma pagina propria para revisar relatorio pronto.
5. Adicionar status de relatorio e historico de envio.
6. Melhorar email para cliente com assunto, mensagem de acompanhamento e identidade Apex/tenant.
7. So entao escrever testes cobrindo o fluxo estabilizado.
