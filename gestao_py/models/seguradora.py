"""Seguradora — substitui a tabela legada `seguradora`."""
from __future__ import annotations

from sqlmodel import Field

from gestao_py.models.base import TabelaBase


class Seguradora(TabelaBase, table=True):
    __tablename__ = "seguradoras"

    nome: str = Field(unique=True)
    ativo: bool = True
