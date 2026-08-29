# Gestão Master Parceria — reescrita em Python (Fase 1)

Reescrita em [Reflex](https://reflex.dev) do sistema legado em `../` (SPA
vanilla JS + Supabase). Contexto completo da decisão de arquitetura e do
que foi corrigido em relação ao legado: `../CODE_REVIEW_2026-08-29.md`,
`SCHEMA_NOTES.md` e `ROADMAP.md` neste diretório.

## Setup

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# depois:
pip install -r requirements.txt

copy .env.example .env
# edite .env se for usar Postgres (senão cai em SQLite local, só para dev)
```

## Popular dados de exemplo

```bash
python -m gestao_py.scripts.seed
```

Cria as tabelas, um usuário `admin` (senha impressa no console) e alguns
registros de exemplo de segurado/apólice.

## Rodar

```bash
reflex run
```

Abre em `http://localhost:3000`.

## Testes

```bash
pytest
```

## Produção

Não use o fallback SQLite em produção. Defina `DATABASE_URL` (Postgres) e
`SECRET_KEY` em `.env` ou nas variáveis de ambiente do servidor, e rode as
migrações versionadas em vez do atalho `rx.Model.create_all()` do seed:

```bash
reflex db init
reflex db makemigrations
reflex db migrate
```
