"""Autorização por nível de acesso (RBAC), checada no servidor.

No legado, `nivelAtual()`/`window.usuarioAtual?.nivel_acesso` só escondiam
botões na UI — qualquer requisição direta contra a API REST do Supabase
(com a anon key, que também estava hardcoded) ignorava essa checagem por
completo. Aqui a autorização mora nos event handlers do backend (chamados
por AuthState/os *_state.py de cada módulo), então não existe caminho para
burlar via DevTools ou chamada direta de API.

Níveis (preservando a semântica observada no legado):
  1-3: operacional (sem acesso a auditoria completa nem campos financeiros travados)
  4:   supervisor (vê a própria auditoria)
  5-6: admin (vê toda auditoria, edita campos financeiros travados)
"""
from __future__ import annotations


class AutorizacaoNegada(Exception):
    """Levantada quando um usuário tenta uma ação além do seu nível de acesso."""


NIVEL_ADMIN_FINANCEIRO = 5
NIVEL_ADMIN_AUDITORIA = 5


def exigir_nivel(nivel_usuario: int, nivel_minimo: int, acao: str = "esta ação") -> None:
    if nivel_usuario < nivel_minimo:
        raise AutorizacaoNegada(
            f"Nível de acesso insuficiente para {acao} "
            f"(necessário >= {nivel_minimo}, usuário tem {nivel_usuario})."
        )


def pode_editar_financeiro_travado(nivel_usuario: int) -> bool:
    return nivel_usuario >= NIVEL_ADMIN_FINANCEIRO


def pode_ver_auditoria_completa(nivel_usuario: int) -> bool:
    return nivel_usuario >= NIVEL_ADMIN_AUDITORIA
