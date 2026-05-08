# Apex

Aplicacao Flask/Dash para pesquisar conteudos, gerar relatorios com IA e enviar resultados por email.

## Requisitos

- Docker
- Docker Compose

Para desenvolvimento local sem Docker, use Python 3.10 e Redis disponivel.

## Setup com Docker

1. Crie o arquivo de ambiente. Para desenvolvimento local com Docker:

```bash
cp .env.development.example .env
```

2. Edite `.env` e troque ao menos:

```bash
SECRET_SESSION=change-me-in-production
```

3. Suba Redis, app e worker:

```bash
docker compose up --build
```

No ambiente de desenvolvimento, `.env.development.example` ativa `COMPOSE_PROFILES=local-db`, entao o Compose tambem sobe um PostgreSQL local em `localhost:5432`.

4. Em outro terminal, aplique as migracoes e crie o tenant padrao:

```bash
docker compose exec apex flask db upgrade
docker compose exec apex flask create-db
```

Sempre rode `flask db upgrade` na primeira subida de um banco novo e depois de atualizar o codigo. O comando `create-db` fica como compatibilidade de desenvolvimento: ele garante o tenant padrao e preenche `tenant_id` em registros antigos.

O erro `sqlite3.OperationalError: no such table: user` indica que as migracoes ainda nao foram executadas para o banco em uso.

Se voce ja tinha um banco criado com `create-db` antes das migracoes formais, primeiro confira um backup e depois marque o schema atual como migrado:

```bash
docker compose exec apex flask backup-database --output /app/data/pre-migrations.backup
docker compose exec apex flask create-db
docker compose exec apex flask db stamp 0001_initial_schema
docker compose exec apex flask db upgrade
```

O comando nao cria mais `admin/admin` automaticamente. Para criar um admin inicial, use:

```bash
docker compose exec apex flask add-user --tenant default --username seu_admin --password sua_senha_forte --admin
```

Para trocar a senha de um usuario existente:

```bash
docker compose exec apex flask set-user-password --tenant default --username seu_admin --password nova_senha_forte
```

Usuarios com `--admin` acessam a area administrativa em:

```text
http://localhost:5000/admin
```

Nessa tela e possivel criar tenants e usuarios por tenant.

5. Acesse:

```text
http://localhost:5000
```

## Setup local sem Docker

1. Entre na pasta da aplicacao:

```bash
cd apex
```

2. Crie e ative um ambiente virtual:

```bash
python3.10 -m venv .venv
source .venv/bin/activate
```

3. Instale as dependencias:

```bash
pip install -r requirements.txt
python -m nltk.downloader punkt
```

4. Exporte as variaveis minimas:

```bash
export ENVIRONMENT=development
export BASE_URL=/
export SECRET_SESSION=dev-secret-session
export REDIS_HOST=redis://localhost:6379
export DATABASE_URL=sqlite:///$PWD/src/database.db
```

5. Crie o banco:

```bash
flask --app wsgi:app db upgrade
flask --app wsgi:app create-db
```

6. Rode a aplicacao:

```bash
python wsgi.py
```

O app local sobe em:

```text
http://localhost:8080
```

## Servicos

- `apex`: aplicacao Flask/Dash via Gunicorn.
- `celery`: worker para gerar relatorios.
- `redis`: sessoes, cache, broker e backend de resultados.
- `postgres`: banco PostgreSQL local, usado apenas quando `COMPOSE_PROFILES=local-db` esta ativo.

## Ambientes

A aplicacao usa `ENVIRONMENT` para separar configuracoes:

- `development`: ambiente local, cookies podem usar HTTP.
- `staging`: homologacao, comportamento proximo de producao.
- `production`: producao, cookies seguros por padrao.

Arquivos de exemplo:

- `.env.development.example`
- `.env.staging.example`
- `.env.production.example`
- `.env.example`, arquivo generico com todas as variaveis principais

Para trocar o ambiente usado pelo Docker Compose, copie o exemplo desejado para `.env`:

```bash
cp .env.staging.example .env
```

Variaveis principais:

- `ENVIRONMENT`: `development`, `staging` ou `production`.
- `SECRET_SESSION`: segredo Flask, deve ser longo e unico por ambiente.
- `CREDENTIALS_SECRET_KEY`: segredo usado para criptografar credenciais sensiveis salvas por usuario; deve ser longo, unico e preservado entre deploys.
- `SESSION_COOKIE_SECURE`: `true` em staging/producao com HTTPS.
- `REDIS_HOST`: URL base do Redis.
- `DATABASE_URL`: URL do banco.
- `COMPOSE_PROFILES`: use `local-db` no desenvolvimento local para subir o Postgres do Compose; deixe vazio em staging/producao quando usar banco externo.
- `BASE_URL`: prefixo/raiz da aplicacao.
- `ROOT_DOMAIN`: dominio raiz usado para resolver tenants por subdominio.
- `DEFAULT_TENANT_SLUG`: tenant usado em localhost ou no dominio raiz.
- `LIMIT`: limite interno usado pela aplicacao.
- `CELERY_RESULT_EXPIRES_SECONDS`: tempo de retencao dos resultados Celery no Redis.
- `CELERY_TASK_SOFT_TIME_LIMIT_SECONDS` e `CELERY_TASK_TIME_LIMIT_SECONDS`: limites das tarefas de relatorio.
- `EXTERNAL_REQUEST_TIMEOUT_SECONDS`, `OPENAI_TIMEOUT_SECONDS` e `SMTP_TIMEOUT_SECONDS`: timeouts das integracoes externas.
- `SEARCH_RESULTS_PER_SOURCE`: limite de resultados retornados por origem na pesquisa.

Em `staging` e `production`, a aplicacao falha na inicializacao se `SECRET_SESSION`, `CREDENTIALS_SECRET_KEY`, `REDIS_HOST` ou `DATABASE_URL` estiverem ausentes/inseguros, ou se `SESSION_COOKIE_SECURE=false`.

## Banco de dados e migracoes

O banco recomendado para producao e PostgreSQL externo, preferencialmente gerenciado pelo provedor de infraestrutura. O `docker-compose.yaml` inclui um PostgreSQL local apenas para desenvolvimento, ativado por `COMPOSE_PROFILES=local-db`.

Em staging/producao, configure `DATABASE_URL` com a URL do banco externo e nao ative o profile `local-db`:

```bash
DATABASE_URL=postgresql://usuario:senha@host-externo:5432/apex_production
```

SQLite continua suportado para testes simples, mas deploys de producao nao devem depender de copiar arquivos `.db`.

Fluxo padrao:

```bash
flask --app wsgi:app db upgrade
```

Para criar uma nova migracao depois de alterar modelos:

```bash
flask --app wsgi:app db migrate -m "descricao curta"
flask --app wsgi:app db upgrade
```

Backups:

```bash
flask --app wsgi:app backup-database --output /caminho/seguro/apex.backup
```

Restore:

```bash
flask --app wsgi:app restore-database --input /caminho/seguro/apex.backup
flask --app wsgi:app db upgrade
```

Para PostgreSQL, os comandos usam `pg_dump` e `pg_restore`; instale os client tools do PostgreSQL no ambiente onde o backup sera executado. Para SQLite, os comandos usam a API nativa de backup do SQLite.

## Multi-tenant por subdominio

A aplicacao resolve o tenant pelo subdominio quando `ROOT_DOMAIN` esta configurado.

Exemplo para producao:

```bash
ROOT_DOMAIN=dominio.com
DEFAULT_TENANT_SLUG=default
```

Com essa configuracao:

- `empresa1.dominio.com` usa o tenant `empresa1`.
- `empresa2.dominio.com` usa o tenant `empresa2`.
- `dominio.com`, `localhost` e `127.0.0.1` usam o tenant definido em `DEFAULT_TENANT_SLUG`.

Crie tenants e usuarios assim:

```bash
docker compose exec apex flask add-tenant --slug empresa1 --name "Empresa 1"
docker compose exec apex flask add-user --tenant empresa1 --username admin_empresa1 --password senha_forte --admin
```

Depois de alterar modelos ou em bancos antigos, rode:

```bash
docker compose exec apex flask db upgrade
docker compose exec apex flask create-db
```

Esse comando cria tabelas novas e preenche o tenant padrao para registros antigos.

Para criptografar credenciais sensiveis ja existentes em bancos antigos:

```bash
docker compose exec apex flask encrypt-credentials
```

## Arquivos importantes

- `.env.example`: variaveis obrigatorias e defaults de desenvolvimento.
- `.env.*.example`: modelos especificos por ambiente.
- `docker-compose.yaml`: stack local da aplicacao.
- `PRODUCAO_ROADMAP.md`: roteiro de melhorias para producao.

## Verificacoes basicas

```bash
python -m compileall apex/src/pages apex/src/callbacks apex/src/utils
git diff --check
```
