"""Log de auditoria — grava em audit_log (substitui a leitura-apenas
`gestao-auditoria.js`; a escrita agora é centralizada aqui em vez de
espalhada/opcional em cada módulo).

Recebe a mesma `Session` usada para gravar a entidade, para que a mudança de
negócio e o registro de auditoria fiquem na mesma transação — se um falhar,
o outro também é revertido (o legado não tinha essa garantia).
"""
from __future__ import annotations

import json
from typing import Any, Optional

from sqlmodel import Session

from gestao_py.models.usuario import AuditLog


def _serializar(dados: Optional[dict[str, Any]]) -> Optional[str]:
    if dados is None:
        return None
    return json.dumps(dados, default=str, ensure_ascii=False)


def log_action(
    session: Session,
    *,
    usuario_id: Optional[int],
    acao: str,
    entidade: str,
    registro_id: Optional[int] = None,
    antes: Optional[dict[str, Any]] = None,
    depois: Optional[dict[str, Any]] = None,
) -> None:
    session.add(
        AuditLog(
            usuario_id=usuario_id,
            acao=acao,
            entidade=entidade,
            registro_id=registro_id,
            dados_antes=_serializar(antes),
            dados_depois=_serializar(depois),
        )
    )
