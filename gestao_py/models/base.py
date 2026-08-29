"""Base compartilhada dos modelos.

Usa `sqlmodel.SQLModel` diretamente, não `reflex.Model` — a partir da
0.9.2 o Reflex marcou `rx.Model` como deprecado ("will be completely
removed in 1.0.0", aviso emitido em tempo de execução), recomendando usar
a camada de ORM (SQLAlchemy/SQLModel) diretamente. `rx.session()` continua
sendo a forma correta de obter uma sessão (não é afetado pela depreciação —
só chama `sqlmodel.Session(get_engine())` internamente), e
`TabelaBase.metadata` é o mesmo objeto que `rx.Model.metadata`, então
`reflex db init/makemigrations/migrate` continua funcionando normalmente
sobre estas tabelas.
"""
from __future__ import annotations

from typing import Optional

from sqlmodel import Field, SQLModel


class TabelaBase(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
