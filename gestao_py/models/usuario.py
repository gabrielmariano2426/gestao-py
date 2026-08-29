"""Usuário, sessão e log de auditoria.

Substitui c02usuario (com a falha crítica corrigida: `senha` em texto plano
vira `senha_hash`, gerado por passlib/bcrypt — ver auth/security.py),
c91usuario_sessoes e c92audit_log.
"""
from __future__ import annotations

import datetime as dt
from typing import Optional

from sqlmodel import Field

from gestao_py.models.base import TabelaBase


class Usuario(TabelaBase, table=True):
    __tablename__ = "usuarios"

    codigo_usr: str = Field(unique=True, index=True)
    nome: str
    apelido: Optional[str] = None
    senha_hash: str
    nivel_acesso: int = 1
    ativo: bool = True
    criado_em: dt.datetime = Field(default_factory=dt.datetime.utcnow)


class UsuarioSessao(TabelaBase, table=True):
    """Sessão de servidor real: um token opaco identifica a linha aqui.

    Substitui o legado, que guardava `{codigo_usr, nome, nivel_acesso, ...}`
    inteiro em `localStorage.usuarioAtual` — qualquer um com acesso ao
    DevTools podia editar `nivel_acesso` no objeto local e nada no servidor
    percebia. Aqui o browser só guarda o token (cookie); todo dado de
    permissão é relido do banco a cada checagem.
    """

    __tablename__ = "usuario_sessoes"

    usuario_id: int = Field(foreign_key="usuarios.id", index=True)
    token: str = Field(unique=True, index=True)
    login_em: dt.datetime = Field(default_factory=dt.datetime.utcnow)
    logout_em: Optional[dt.datetime] = None
    ip: Optional[str] = None


class AuditLog(TabelaBase, table=True):
    """Log de auditoria append-only — toda escrita sensível deve gravar aqui.

    Estabelece o padrão (`services/audit.py:log_action`) que os módulos das
    fases seguintes (assinatura, automações, trello, financeiro) também
    devem seguir, em vez de deixar auditoria como funcionalidade só de
    leitura (como está no legado `gestao-auditoria.js`).
    """

    __tablename__ = "audit_log"

    usuario_id: Optional[int] = Field(default=None, foreign_key="usuarios.id", index=True)
    acao: str = Field(index=True)  # create | update | delete | login | ...
    entidade: str = Field(index=True)  # "segurado" | "seguro" | ...
    registro_id: Optional[int] = Field(default=None, index=True)
    dados_antes: Optional[str] = None  # JSON serializado
    dados_depois: Optional[str] = None  # JSON serializado
    criado_em: dt.datetime = Field(default_factory=dt.datetime.utcnow, index=True)
