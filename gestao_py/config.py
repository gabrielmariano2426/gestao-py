"""Configuração central da aplicação — único lugar que lê segredos do ambiente.

Nenhum valor sensível (chave de banco, token de API, salt) deve existir como
literal em código em nenhum outro arquivo do projeto. Isso corrige o achado
mais grave da revisão do sistema legado: chaves do Supabase hardcoded em
`api/enviar-email.js` e `api/doc.js`.
"""
from __future__ import annotations

import os
import secrets

from dotenv import load_dotenv

load_dotenv()


def _require(name: str, default: str | None = None) -> str:
    value = os.environ.get(name, default)
    if value is None:
        raise RuntimeError(
            f"Variável de ambiente ausente: {name}. Defina em um arquivo .env "
            f"(veja .env.example) ou no ambiente do processo."
        )
    return value


# Banco de dados: Postgres em produção (DATABASE_URL). Sem essa variável,
# cai para um SQLite local — só serve para desenvolvimento rápido, nunca
# para produção (não segura escrita concorrente nem tipos avançados).
DATABASE_URL: str = os.environ.get("DATABASE_URL", "sqlite:///gestao.db")
IS_SQLITE_DEV: bool = DATABASE_URL.startswith("sqlite")

# Segredo usado para assinar tokens de sessão e o hash de sufixo de
# documentos (substitui o SALT hardcoded do legado em api/doc.js).
SECRET_KEY: str = os.environ.get("SECRET_KEY") or secrets.token_urlsafe(32)

# Integrações externas (todas opcionais nesta fase — usadas por services/).
RESEND_API_KEY: str | None = os.environ.get("RESEND_API_KEY")
ANTHROPIC_API_KEY: str | None = os.environ.get("ANTHROPIC_API_KEY")
CPFCNPJ_TOKEN: str | None = os.environ.get("CPFCNPJ_TOKEN")

# Nome da empresa exibido na UI (branding), configurável sem tocar em código.
APP_NAME: str = os.environ.get("APP_NAME", "Master Parceria — Gestão")
