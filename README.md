# Apex

Aplicacao Flask/Dash para pesquisar conteudos, gerar relatorios com IA e enviar resultados por email.

## Requisitos

- Docker
- Docker Compose

Para desenvolvimento local sem Docker, use Python 3.10 e Redis disponivel.

## Setup com Docker

1. Crie o arquivo de ambiente:

```bash
cp .env.example .env
```

2. Edite `.env` e troque ao menos:

```bash
SECRET_SESSION=change-me-in-production
```

3. Suba Redis, app e worker:

```bash
docker compose up --build
```

4. Em outro terminal, crie as tabelas e o usuario admin inicial:

```bash
docker compose exec apex flask create-db
```

O usuario criado pelo comando atual e:

- usuario: `admin`
- senha: `admin`

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

## Arquivos importantes

- `.env.example`: variaveis obrigatorias e defaults de desenvolvimento.
- `docker-compose.yaml`: stack local da aplicacao.
- `PRODUCAO_ROADMAP.md`: roteiro de melhorias para producao.

## Verificacoes basicas

```bash
python -m compileall apex/src/pages apex/src/callbacks apex/src/utils
git diff --check
```
